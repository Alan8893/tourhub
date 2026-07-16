from dataclasses import dataclass
from uuid import uuid4

from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerationResult,
    MealPlanGenerator,
)
from app.engines.meal_schedule import MealScheduleEngine
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM


@dataclass(frozen=True)
class SavedMealPlanResult:
    meal_plan: MealPlanORM
    warnings: list[str]


class MealPlanService:
    """Application service for meal plan generation."""

    def __init__(self, dish_repository, meal_plan_repository=None, generator=None, schedule_engine=None):
        self.dish_repository = dish_repository
        self.meal_plan_repository = meal_plan_repository
        self.generator = generator or MealPlanGenerator()
        self.schedule_engine = schedule_engine or MealScheduleEngine()

    def generate(self, days: int, meals_per_day: list[str]) -> MealPlanGenerationResult:
        return self.generator.generate(
            dishes=self._generation_dishes(),
            days=days,
            meals_per_day=meals_per_day,
        )

    def generate_and_save(
        self,
        name: str,
        participants: int,
        days: int,
        meals_per_day: list[str],
        project_id: int | None = None,
        start_meal: str | None = None,
        end_meal: str | None = None,
    ) -> MealPlanORM:
        return self.generate_and_save_result(
            name=name,
            participants=participants,
            days=days,
            meals_per_day=meals_per_day,
            project_id=project_id,
            start_meal=start_meal,
            end_meal=end_meal,
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
    ) -> SavedMealPlanResult:
        if self.meal_plan_repository is None:
            raise ValueError("MealPlanRepository is required")

        dishes = self._generation_dishes()
        if start_meal and end_meal:
            schedule = self.schedule_engine.build(
                days=days,
                start_meal=start_meal,
                end_meal=end_meal,
            )
            result = self.generator.generate(
                dishes=dishes,
                days=days,
                schedule=schedule,
            )
        else:
            result = self.generator.generate(
                dishes=dishes,
                days=days,
                meals_per_day=meals_per_day,
            )

        meal_plan = MealPlanORM(
            id=str(uuid4()),
            project_id=project_id,
            name=name,
            participants=participants,
            days_count=days,
        )
        self.meal_plan_repository.add(meal_plan)

        days_map: dict[int, MealPlanDayORM] = {}
        for item in result.items:
            day = self._get_or_create_day(meal_plan, days_map, item.day_number)
            self.meal_plan_repository.add_item(
                MealPlanItemORM(
                    id=str(uuid4()),
                    day=day,
                    dish_id=item.dish_id,
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
            )
            self.meal_plan_repository.add_slot(meal_slot)

            for index, dish in enumerate(slot.dishes):
                self.meal_plan_repository.add_slot_dish(
                    MealSlotDishORM(
                        id=str(uuid4()),
                        slot=meal_slot,
                        dish_id=dish.id,
                        order=index,
                    )
                )

        self.meal_plan_repository.commit()
        loaded_meal_plan = self.meal_plan_repository.get_with_details(meal_plan.id)
        if loaded_meal_plan is None:
            raise ValueError(f"Meal plan not found after save: {meal_plan.id}")
        return SavedMealPlanResult(
            meal_plan=loaded_meal_plan,
            warnings=result.warnings,
        )

    def _generation_dishes(self) -> list[DishInput]:
        generation_dishes: list[DishInput] = []
        for dish in self.dish_repository.list():
            recipe = getattr(dish, "recipe", None)
            if recipe is not None and getattr(recipe, "is_archived", False):
                continue

            assignments = tuple(
                DishRoleInput(
                    role=meal_role.role,
                    is_repeatable=meal_role.is_repeatable,
                    allowed_meal_types=frozenset(
                        meal_type.meal_type for meal_type in meal_role.meal_types
                    ),
                )
                for meal_role in dish.meal_roles
            )
            generation_dishes.append(
                DishInput(
                    id=dish.id,
                    name=dish.name,
                    meal_roles=assignments,
                )
            )
        return generation_dishes

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
