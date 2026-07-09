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
        self.shopping_list_service = shopping_list_service

    def calculate(
        self,
        meal_plan: MealPlanORM,
    ) -> ShoppingListResult:
        recipes = self._collect_recipes(meal_plan)

        return self.shopping_list_service.calculate_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            days=meal_plan.days_count,
        )

    def calculate_packaged(
        self,
        meal_plan: MealPlanORM,
    ) -> PackagedShoppingResult:
        recipes = self._collect_recipes(meal_plan)

        return self.shopping_list_service.calculate_packaged_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            days=meal_plan.days_count,
        )

    def _collect_recipes(
        self,
        meal_plan: MealPlanORM,
    ) -> list:
        """
        Collect unique recipes from meal plan.

        New source:
            MealSlot -> MealSlotDish -> Dish -> Recipe

        Legacy fallback:
            MealPlanItem -> Dish -> Recipe
        """

        recipes = []
        seen_recipe_ids = set()

        def add_recipe(recipe):
            if not recipe:
                return

            if recipe.id in seen_recipe_ids:
                return

            seen_recipe_ids.add(recipe.id)
            recipes.append(recipe)

        for day in meal_plan.days:
            # New MealSlot based composition
            for slot in day.slots:
                for slot_dish in slot.dishes:
                    if not slot_dish.dish:
                        continue

                    add_recipe(slot_dish.dish.recipe)

            # Legacy compatibility
            for item in day.items:
                if not item.dish:
                    continue

                add_recipe(item.dish.recipe)

        return recipes
