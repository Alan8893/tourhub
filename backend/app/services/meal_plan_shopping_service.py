from app.models.meal_plan import MealPlanORM

from app.services.shopping_list_service import (
    ShoppingListService,
)

from app.engines.shopping_list import (
    ShoppingListResult,
)

from app.engines.packaging import (
    PackagedShoppingResult,
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

        recipes = self._collect_recipes(
            meal_plan
        )

        return (
            self.shopping_list_service
            .calculate_for_recipes(
                recipes=recipes,
                people=meal_plan.participants,
                days=meal_plan.days_count,
            )
        )

    def calculate_packaged(
        self,
        meal_plan: MealPlanORM,
    ) -> PackagedShoppingResult:
        """
        Calculate shopping list
        with package information.
        """

        recipes = self._collect_recipes(
            meal_plan
        )

        return (
            self.shopping_list_service
            .calculate_packaged_for_recipes(
                recipes=recipes,
                people=meal_plan.participants,
                days=meal_plan.days_count,
            )
        )

    def _collect_recipes(
        self,
        meal_plan: MealPlanORM,
    ) -> list:
        """
        Collect unique recipes from meal plan.
        """

        recipes = []

        seen_recipe_ids = set()

        for day in meal_plan.days:

            for item in day.items:

                if not item.dish:
                    continue

                recipe = item.dish.recipe

                if not recipe:
                    continue

                if recipe.id in seen_recipe_ids:
                    continue

                seen_recipe_ids.add(
                    recipe.id
                )

                recipes.append(
                    recipe
                )

        return recipes