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

from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository


class MealPlanService:
    """Application service for meal plan generation."""

    def __init__(
        self,
        dish_repository: DishRepository,
        meal_plan_repository: MealPlanRepository | None = None,
        generator: MealPlanGenerator | None = None,
        schedule_engine: MealScheduleEngine | None = None,
    ):
        self.dish_repository = dish_repository
        self.meal_plan_repository = meal_plan_repository
        self.generator = generator or MealPlanGenerator()
        self.schedule_engine = schedule_engine or MealScheduleEngine()

    def generate(
        self,
        days: int,
        meals_per_day: list[str],
    ) -> MealPlanGenerationResult:
        dishes = self.dish_repository.list()

        dish_inputs = [
            DishInput(
                id=dish.id,
                name=dish.name,
            )
            for dish in dishes
        ]

        return self.generator.generate(
            dishes=dish_inputs,
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
        start_meal: str = "breakfast",
        end_meal: str = "dinner",
    ) -> MealPlanORM:
        if self.meal_plan_repository is None:
            raise ValueError("MealPlanRepository is required")

        dishes = self.dish_repository.list()

        dish_inputs = [
            DishInput(
                id=dish.id,
                name=dish.name,
            )
            for dish in dishes
        ]

        schedule = self.schedule_engine.build(
            days=days,
            start_meal=start_meal,
            end_meal=end_meal,
        )

        result = self.generator.generate(
            dishes=dish_inputs,
            days=days,
            schedule=schedule,
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
            if item.day_number not in days_map:
                day = MealPlanDayORM(
                    id=str(uuid4()),
                    day_number=item.day_number,
                    meal_plan=meal_plan,
                )
                days_map[item.day_number] = day
                self.meal_plan_repository.add_day(day)

            meal_item = MealPlanItemORM(
                id=str(uuid4()),
                day=days_map[item.day_number],
                dish_id=item.dish_id,
                meal_type=item.meal_type,
            )

            self.meal_plan_repository.add_item(meal_item)

        self.meal_plan_repository.commit()

        loaded_meal_plan = self.meal_plan_repository.get_with_details(meal_plan.id)

        if loaded_meal_plan is None:
            raise ValueError(f"Meal plan not found after save: {meal_plan.id}")

        return loaded_meal_plan
