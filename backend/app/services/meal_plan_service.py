from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerationResult,
    MealPlanGenerator,
)

from app.repositories.dish_repository import DishRepository


class MealPlanService:
    """
    Application service for meal plan generation.

    Coordinates:

    Repository
        |
        Generator
    """

    def __init__(
        self,
        dish_repository: DishRepository,
        generator: MealPlanGenerator | None = None,
    ):
        self.dish_repository = dish_repository

        self.generator = generator or MealPlanGenerator()

    def generate(
        self,
        days: int,
        meals_per_day: list[str],
    ) -> MealPlanGenerationResult:
        """
        Generate meal plan from available dishes.
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