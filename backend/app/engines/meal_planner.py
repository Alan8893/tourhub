from collections import defaultdict
from typing import List, Dict


class MealPlannerEngine:
    """
    Core domain engine for meal planning.

    Responsibilities:
    - generate menu rotation
    - calculate shopping list
    - aggregate ingredients
    """

    def __init__(self, recipes: Dict[str, object], dishes: Dict[str, object]):
        """
        recipes: dict[recipe_id -> RecipeORM or Recipe]
        dishes: dict[dish_id -> DishORM or Dish]
        """
        self.recipes = recipes
        self.dishes = dishes

    def generate_meal_plan(
        self,
        dish_ids: List[str],
        days: int,
        participants: int
    ) -> Dict:
        """
        Generate meal plan + shopping list.
        """

        if not dish_ids:
            raise ValueError("dish_ids cannot be empty")

        selected_dishes = []

        # 1. ROTATION LOGIC (simple MVP version)
        for i in range(days):
            dish_id = dish_ids[i % len(dish_ids)]

            dish = self.dishes.get(dish_id)
            if not dish:
                raise ValueError(f"Dish not found: {dish_id}")

            selected_dishes.append(dish)

        # 2. SHOPPING LIST
        shopping_list = self._calculate_shopping_list(
            selected_dishes,
            participants
        )

        return {
            "days": days,
            "participants": participants,
            "dishes": [getattr(d, "name", str(d)) for d in selected_dishes],
            "shopping_list": shopping_list
        }

    def _calculate_shopping_list(
        self,
        dishes: List[object],
        participants: int
    ) -> Dict[str, float]:

        result = defaultdict(float)

        for dish in dishes:
            recipe_id = getattr(dish, "recipe_id", None)

            if not recipe_id:
                continue

            recipe = self.recipes.get(recipe_id)
            if not recipe:
                continue

            ingredients = getattr(recipe, "ingredients", {})

            # ingredients: {product_id: amount_per_person}
            for product_id, amount_per_person in ingredients.items():
                result[product_id] += amount_per_person * participants

        return dict(result)