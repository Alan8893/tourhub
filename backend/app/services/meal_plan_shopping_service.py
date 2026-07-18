from typing import Any

from app.engines.packaging import PackagedShoppingResult
from app.engines.shopping_list import ShoppingListResult
from app.models.meal_plan import MealPlanORM
from app.services.shopping_list_service import ShoppingListService


class MealPlanShoppingService:
    """Calculate shopping requirements from persisted assignment Recipes."""

    def __init__(self, shopping_list_service: ShoppingListService):
        self.shopping_list_service = shopping_list_service

    def calculate(self, meal_plan: MealPlanORM) -> ShoppingListResult:
        recipes = self._collect_recipe_occurrences(meal_plan)
        return self.shopping_list_service.calculate_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            days=1,
        )

    def calculate_packaged(self, meal_plan: MealPlanORM) -> PackagedShoppingResult:
        recipes = self._collect_recipe_occurrences(meal_plan)
        return self.shopping_list_service.calculate_packaged_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            days=1,
        )

    def _collect_recipe_occurrences(self, meal_plan: MealPlanORM) -> list[Any]:
        """Collect the selected Recipe for every persisted dish occurrence."""
        recipes: list[Any] = []
        for day in meal_plan.days:
            if day.slots:
                recipes.extend(
                    slot_dish.recipe
                    for slot in day.slots
                    for slot_dish in slot.dishes
                    if slot_dish.recipe is not None
                )
                continue
            recipes.extend(item.recipe for item in day.items if item.recipe is not None)
        return recipes

    def _collect_recipes(self, meal_plan: MealPlanORM) -> list[Any]:
        return self._collect_recipe_occurrences(meal_plan)
