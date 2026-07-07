from uuid import uuid4

from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerationResult,
    MealPlanGenerator,
)

from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM

from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository


class MealPlanService:
    """
    Application service for meal plan generation.

    Coordinates:

    Repository
        |
        Generator
        |
        Persistence
    """

    def __init__(
        self,
        dish_repository: DishRepository,
        meal_plan_repository: MealPlanRepository | None = None,
        generator: MealPlanGenerator | None = None,
    ):
        self.dish_repository = dish_repository
        self.meal_plan_repository = meal_plan_repository
        self.generator = generator or MealPlanGenerator()

    def generate(
        self,
        days: int,
        meals_per_day: list[str],
    ) -> MealPlanGenerationResult:
        """
        Generate meal plan without persistence.
        """

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
    ) -> MealPlanORM:
        """
        Generate meal plan and persist it.
        """

        if self.meal_plan_repository is None:
            raise ValueError(
                "MealPlanRepository is required"
            )

        result = self.generate(
            days=days,
            meals_per_day=meals_per_day,
        )

        meal_plan = MealPlanORM(
            id=str(uuid4()),
            name=name,
            participants=participants,
            days_count=days,
        )

        self.meal_plan_repository.add(
            meal_plan
        )

        days_map: dict[int, MealPlanDayORM] = {}

        for item in result.items:
            if item.day_number not in days_map:
                day = MealPlanDayORM(
                    id=str(uuid4()),
                    day_number=item.day_number,
                    meal_plan=meal_plan,
                )

                days_map[item.day_number] = day

                self.meal_plan_repository.add_day(
                    day
                )

            meal_item = MealPlanItemORM(
                id=str(uuid4()),
                day=days_map[item.day_number],
                dish_id=item.dish_id,
                meal_type=item.meal_type,
            )

            self.meal_plan_repository.add_item(
                meal_item
            )

        self.meal_plan_repository.commit()

        return meal_plan