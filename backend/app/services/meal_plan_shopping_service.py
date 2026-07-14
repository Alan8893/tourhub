from app.engines.packaging import PackagedShoppingResult
from app.engines.shopping_list import ShoppingListResult
from app.models.meal_plan import MealPlanORM
from app.services.shopping_list_service import ShoppingListService


class MealPlanShoppingService:
    """Calculate shopping requirements from the current meal-plan composition."""

    def __init__(self, shopping_list_service: ShoppingListService):
        self.shopping_list_service = shopping_list_service

    def calculate(self, meal_plan: MealPlanORM) -> ShoppingListResult:
        recipes = self._collect_recipe_occurrences(meal_plan)

        return self.shopping_list_service.calculate_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            # Recipe occurrences already encode the exact trip-day frequency.
            days=1,
        )

    def calculate_packaged(self, meal_plan: MealPlanORM) -> PackagedShoppingResult:
        recipes = self._collect_recipe_occurrences(meal_plan)

        return self.shopping_list_service.calculate_packaged_for_recipes(
            recipes=recipes,
            people=meal_plan.participants,
            # Recipe occurrences already encode the exact trip-day frequency.
            days=1,
        )

    def _collect_recipe_occurrences(self, meal_plan: MealPlanORM) -> list:
        """Collect one recipe entry for every dish occurrence in the menu.

        MealSlot is the canonical composition source. Legacy MealPlanItem records
        are read only for days without slots, preventing double counting during
        the evolutionary migration.
        """

        recipes = []

        for day in meal_plan.days:
            if day.slots:
                for slot in day.slots:
                    for slot_dish in slot.dishes:
                        dish = slot_dish.dish
                        if dish and dish.recipe:
                            recipes.append(dish.recipe)
                continue

            for item in day.items:
                if item.dish and item.dish.recipe:
                    recipes.append(item.dish.recipe)

        return recipes

    # Compatibility for existing callers and tests while the old private name is
    # phased out. It now returns occurrences rather than unique recipes.
    def _collect_recipes(self, meal_plan: MealPlanORM) -> list:
        return self._collect_recipe_occurrences(meal_plan)
