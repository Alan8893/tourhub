from uuid import uuid4

from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerationResult,
    MealPlanGenerator,
)
from app.engines.meal_schedule import MealScheduleEngine

from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM


class MealPlanService:
    """Application service for meal plan generation."""

    def __init__(self, dish_repository, meal_plan_repository=None, generator=None, schedule_engine=None):
        self.dish_repository = dish_repository
        self.meal_plan_repository = meal_plan_repository
        self.generator = generator or MealPlanGenerator()
        self.schedule_engine = schedule_engine or MealScheduleEngine()

    def generate(self, days: int, meals_per_day: list[str]) -> MealPlanGenerationResult:
        dishes = [
            DishInput(id=dish.id, name=dish.name)
            for dish in self.dish_repository.list()
        ]

        return self.generator.generate(
            dishes=dishes,
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
        if self.meal_plan_repository is None:
            raise ValueError("MealPlanRepository is required")

        dishes = [
            DishInput(id=dish.id, name=dish.name)
            for dish in self.dish_repository.list()
        ]

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

        days_map = {}

        for item in result.items:
            if item.day_number not in days_map:
                day = MealPlanDayORM(
                    id=str(uuid4()),
                    day_number=item.day_number,
                    meal_plan=meal_plan,
                )
                days_map[item.day_number] = day
                self.meal_plan_repository.add_day(day)

            self.meal_plan_repository.add_item(
                MealPlanItemORM(
                    id=str(uuid4()),
                    day=days_map[item.day_number],
                    dish_id=item.dish_id,
                    meal_type=item.meal_type,
                )
            )

        for slot in result.slots:
            if slot.day_number not in days_map:
                day = MealPlanDayORM(
                    id=str(uuid4()),
                    day_number=slot.day_number,
                    meal_plan=meal_plan,
                )
                days_map[slot.day_number] = day
                self.meal_plan_repository.add_day(day)

            meal_slot = MealSlotORM(
                id=str(uuid4()),
                day=days_map[slot.day_number],
                meal_type=slot.meal_type,
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

        return loaded_meal_plan
