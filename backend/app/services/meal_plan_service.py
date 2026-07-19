from dataclasses import dataclass, replace
from typing import cast
from uuid import uuid4

from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerationResult,
    MealPlanGenerator,
    MealPlanItemResult,
    MealSlotResult,
    PreservedMealSlotInput,
)
from app.engines.meal_schedule import MealScheduleEngine
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.user import UserORM
from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.dish_recipe_variant_service import DishRecipeVariantService


@dataclass(frozen=True)
class SavedMealPlanResult:
    meal_plan: MealPlanORM
    warnings: list[str]


class MealPlanService:
    """Application service for meal plan generation."""

    def __init__(
        self,
        dish_repository: DishRepository,
        meal_plan_repository: MealPlanRepository | None = None,
        generator: MealPlanGenerator | None = None,
        schedule_engine: MealScheduleEngine | None = None,
        actor: UserORM | None = None,
    ) -> None:
        self.dish_repository = dish_repository
        self.meal_plan_repository = meal_plan_repository
        self.generator = generator or MealPlanGenerator()
        self.schedule_engine = schedule_engine or MealScheduleEngine()
        self.actor = actor

    @staticmethod
    def _dish_input(dish, recipe_id: str | None = None) -> DishInput:
        roles = tuple(
            DishRoleInput(
                role=assignment.role,
                is_repeatable=assignment.is_repeatable,
                allowed_meal_types=tuple(
                    item.meal_type for item in assignment.meal_types
                ),
            )
            for assignment in getattr(dish, "meal_roles", [])
        )
        return DishInput(
            id=dish.id,
            name=dish.name,
            meal_roles=roles,
            recipe_id=recipe_id,
        )

    def _variant_map(self, mode: str) -> dict[str, list[RecipeORM]]:
        return {
            dish.id: DishRecipeVariantService.ordered_for_generation(
                dish,
                self.actor,
                mode,
            )
            for dish in self.dish_repository.list()
        }

    def _generation_dishes(
        self,
        variant_map: dict[str, list[RecipeORM]],
    ) -> list[DishInput]:
        return [
            self._dish_input(dish)
            for dish in self.dish_repository.list()
            if variant_map.get(dish.id)
        ]

    def _preserved_slots(
        self,
        meal_plan: MealPlanORM | None,
    ) -> list[PreservedMealSlotInput]:
        if meal_plan is None:
            return []

        result: list[PreservedMealSlotInput] = []
        for day in cast(list[MealPlanDayORM], meal_plan.days):
            for slot in cast(list[MealSlotORM], day.slots):
                if not slot.is_manually_edited:
                    continue
                slot_dishes = cast(list[MealSlotDishORM], slot.dishes)
                result.append(
                    PreservedMealSlotInput(
                        day_number=day.day_number,
                        meal_type=slot.meal_type,
                        dishes=[
                            self._dish_input(item.dish, recipe_id=item.recipe_id)
                            for item in slot_dishes
                        ],
                    )
                )
        return result

    @staticmethod
    def _assign_recipe_variants(
        result: MealPlanGenerationResult,
        variant_map: dict[str, list[RecipeORM]],
    ) -> MealPlanGenerationResult:
        counters: dict[str, int] = {}
        selected_by_key: dict[tuple[int, str, str], str] = {}
        slots: list[MealSlotResult] = []

        for slot in result.slots:
            selected_dishes: list[DishInput] = []
            for dish in slot.dishes:
                recipe_id = dish.recipe_id
                if recipe_id is None:
                    variants = variant_map.get(dish.id, [])
                    if not variants:
                        raise ValueError(f"No eligible recipe variants for dish: {dish.id}")
                    index = counters.get(dish.id, 0)
                    recipe_id = variants[index % len(variants)].id
                    counters[dish.id] = index + 1
                selected = replace(dish, recipe_id=recipe_id)
                selected_dishes.append(selected)
                selected_by_key[(slot.day_number, slot.meal_type, dish.id)] = recipe_id
            slots.append(replace(slot, dishes=selected_dishes))

        items = [
            replace(
                item,
                recipe_id=(
                    item.recipe_id
                    or selected_by_key[(item.day_number, item.meal_type, item.dish_id)]
                ),
            )
            for item in result.items
        ]
        return MealPlanGenerationResult(
            items=items,
            slots=slots,
            warnings=list(result.warnings),
        )

    def generate(
        self,
        days: int,
        meals_per_day: list[str],
        recipe_generation_mode: str = RecipeGenerationMode.CLUB_ONLY.value,
    ) -> MealPlanGenerationResult:
        variant_map = self._variant_map(recipe_generation_mode)
        generated = self.generator.generate(
            dishes=self._generation_dishes(variant_map),
            days=days,
            meals_per_day=meals_per_day,
            role_aware=True,
        )
        return self._assign_recipe_variants(generated, variant_map)

    def generate_and_save(
        self,
        name: str,
        participants: int,
        days: int,
        meals_per_day: list[str],
        project_id: int | None = None,
        start_meal: str | None = None,
        end_meal: str | None = None,
        recipe_generation_mode: str = RecipeGenerationMode.CLUB_ONLY.value,
        *,
        commit: bool = True,
    ) -> MealPlanORM:
        return self.generate_and_save_result(
            name=name,
            participants=participants,
            days=days,
            meals_per_day=meals_per_day,
            project_id=project_id,
            start_meal=start_meal,
            end_meal=end_meal,
            recipe_generation_mode=recipe_generation_mode,
            commit=commit,
        ).meal_plan

    def generate_and_save_result(
        self,
        name: str,
        participants: int,
        days: int,
        meals_per_day: list[str],
        project_id: int | None = None,
        start_meal: str | None = None,
        end_meal: str | None = None,
        recipe_generation_mode: str = RecipeGenerationMode.CLUB_ONLY.value,
        *,
        commit: bool = True,
    ) -> SavedMealPlanResult:
        if self.meal_plan_repository is None:
            raise ValueError("MealPlanRepository is required")
        RecipeGenerationMode(recipe_generation_mode)

        existing_plan = None
        if project_id is not None:
            current_plan = self.meal_plan_repository.get_by_project_id(project_id)
            if current_plan is not None:
                existing_plan = self.meal_plan_repository.get_with_details(current_plan.id)
                if existing_plan is None:
                    raise ValueError(
                        f"Meal plan not found before regeneration: {current_plan.id}"
                    )

        variant_map = self._variant_map(recipe_generation_mode)
        dishes = self._generation_dishes(variant_map)
        preserved_slots = self._preserved_slots(existing_plan)
        if start_meal and end_meal:
            schedule = self.schedule_engine.build(
                days=days,
                start_meal=start_meal,
                end_meal=end_meal,
            )
            generated = self.generator.generate(
                dishes=dishes,
                days=days,
                schedule=schedule,
                role_aware=True,
                preserved_slots=preserved_slots,
            )
        else:
            generated = self.generator.generate(
                dishes=dishes,
                days=days,
                meals_per_day=meals_per_day,
                role_aware=True,
                preserved_slots=preserved_slots,
            )
        result = self._assign_recipe_variants(generated, variant_map)

        if existing_plan is None:
            meal_plan = MealPlanORM(
                id=str(uuid4()),
                project_id=project_id,
                name=name,
                participants=participants,
                days_count=days,
            )
            self.meal_plan_repository.add(meal_plan)
        else:
            meal_plan = existing_plan
            meal_plan.name = name
            meal_plan.participants = participants
            meal_plan.days_count = days
            cast(list[MealPlanDayORM], meal_plan.days).clear()

        meal_plan.warnings = list(result.warnings)

        days_map: dict[int, MealPlanDayORM] = {}
        for item in result.items:
            if item.recipe_id is None:
                raise ValueError("Generated meal-plan item has no selected recipe")
            day = self._get_or_create_day(meal_plan, days_map, item.day_number)
            self.meal_plan_repository.add_item(
                MealPlanItemORM(
                    id=str(uuid4()),
                    day=day,
                    dish_id=item.dish_id,
                    recipe_id=item.recipe_id,
                    meal_type=item.meal_type,
                )
            )

        slot_order_by_day: dict[int, int] = {}
        for slot in result.slots:
            day = self._get_or_create_day(meal_plan, days_map, slot.day_number)
            slot_order = slot_order_by_day.get(slot.day_number, 0)
            slot_order_by_day[slot.day_number] = slot_order + 1
            meal_slot = MealSlotORM(
                id=str(uuid4()),
                day=day,
                meal_type=slot.meal_type,
                order=slot_order,
                is_manually_edited=slot.is_manually_edited,
            )
            self.meal_plan_repository.add_slot(meal_slot)

            for index, dish in enumerate(slot.dishes):
                if dish.recipe_id is None:
                    raise ValueError("Generated meal-slot dish has no selected recipe")
                self.meal_plan_repository.add_slot_dish(
                    MealSlotDishORM(
                        id=str(uuid4()),
                        slot=meal_slot,
                        dish_id=dish.id,
                        recipe_id=dish.recipe_id,
                        order=index,
                    )
                )

        if commit:
            self.meal_plan_repository.commit()
        else:
            self.meal_plan_repository.flush()
        loaded_meal_plan = self.meal_plan_repository.get_with_details(meal_plan.id)
        if loaded_meal_plan is None:
            raise ValueError(f"Meal plan not found after save: {meal_plan.id}")
        return SavedMealPlanResult(
            meal_plan=loaded_meal_plan,
            warnings=list(loaded_meal_plan.warnings),
        )

    def _get_or_create_day(
        self,
        meal_plan: MealPlanORM,
        days_map: dict[int, MealPlanDayORM],
        day_number: int,
    ) -> MealPlanDayORM:
        day = days_map.get(day_number)
        if day is not None:
            return day

        day = MealPlanDayORM(
            id=str(uuid4()),
            day_number=day_number,
            meal_plan=meal_plan,
        )
        days_map[day_number] = day
        self.meal_plan_repository.add_day(day)
        return day
