from sqlalchemy.orm import Session

from app.engines.shopping_list import (
    IngredientInput,
    ShoppingListResult,
    calculate_shopping_list,
)

from app.models.recipe import RecipeORM


class ShoppingListService:
    """
    Service layer for shopping list generation.

    Responsible for:
    - loading domain data
    - preparing engine input
    - executing calculation
    """

    def __init__(self, session: Session):
        self.session = session


    def calculate_for_recipe(
        self,
        recipe_id: str,
        people: int,
        days: int,
    ) -> ShoppingListResult:
        """
        Calculate required products for recipe.
        """

        recipe = (
            self.session.query(RecipeORM)
            .filter(
                RecipeORM.id == recipe_id
            )
            .first()
        )

        if not recipe:
            raise ValueError(
                f"Recipe not found: {recipe_id}"
            )

        ingredients = []

        for ingredient in recipe.ingredients:

            ingredients.append(
                IngredientInput(
                    product_name=ingredient.product.name,
                    amount_per_person=ingredient.amount_per_person,
                    unit=ingredient.product.unit,
                )
            )

        return calculate_shopping_list(
            people=people,
            days=days,
            ingredients=ingredients,
        )