from app.models.meal_plan import MealPlanORM

from app.services.shopping_list_service import (
    ShoppingListService,
)

from app.engines.shopping_list import (
    ShoppingListResult,
)


class MealPlanShoppingService:
    """
    Generates shopping list from meal plan.

    Responsibility:

    MealPlan
        ↓
    collect recipes
        ↓
    ShoppingListService
        ↓
    ShoppingListResult
    """

    def __init__(
        self,
        shopping_list_service: ShoppingListService,
    ):
        self.shopping_list_service = (
            shopping_list_service
        )

    def calculate(
        self,
        meal_plan: MealPlanORM,
    ) -> ShoppingListResult:
        """
        Calculate shopping list
        for generated meal plan.
        """

        recipes = []

        for day in meal_plan.days:

            for item in day.items:

                if not item.dish:
                    continue

                if not item.dish.recipe:
                    continue

                recipes.append(
                    item.dish.recipe
                )

        return (
            self.shopping_list_service
            .calculate_for_recipes(
                recipes=recipes,
                people=meal_plan.participants,
                days=meal_plan.days_count,
            )
        )