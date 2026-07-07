from sqlalchemy.orm import Session

from app.engines.shopping_list import (
    IngredientInput,
    ShoppingListResult,
    calculate_shopping_list,
)

from app.engines.packaging import (
    PackagingInput,
    PackagedShoppingResult,
    calculate_packages,
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

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def calculate_for_recipe(
        self,
        recipe_id: str,
        people: int,
        days: int,
    ) -> ShoppingListResult:
        """
        Calculate required products for one recipe.
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

        return self.calculate_for_recipes(
            recipes=[recipe],
            people=people,
            days=days,
        )

    def calculate_for_recipes(
        self,
        recipes: list[RecipeORM],
        people: int,
        days: int,
    ) -> ShoppingListResult:
        """
        Calculate required products
        for multiple recipes.
        """

        ingredients = (
            self._build_ingredient_inputs(
                recipes
            )
        )

        return calculate_shopping_list(
            people=people,
            days=days,
            ingredients=ingredients,
        )

    def calculate_packaged_for_recipes(
        self,
        recipes: list[RecipeORM],
        people: int,
        days: int,
    ) -> PackagedShoppingResult:
        """
        Calculate shopping list with packaging.

        Products without package_size
        are skipped from packaging calculation.
        """

        ingredient_inputs = (
            self._build_ingredient_inputs(
                recipes
            )
        )

        base_result = calculate_shopping_list(
            people=people,
            days=days,
            ingredients=ingredient_inputs,
        )

        package_sizes: dict[str, int] = (
            self._collect_package_sizes(
                recipes
            )
        )

        packaging_inputs: list[
            PackagingInput
        ] = []

        for item in base_result.items:

            package_size = package_sizes.get(
                item.product_name
            )

            if not package_size:
                continue

            packaging_inputs.append(
                PackagingInput(
                    product_name=item.product_name,
                    amount=item.amount,
                    unit=item.unit,
                    package_size=package_size,
                )
            )

        return calculate_packages(
            packaging_inputs
        )

    def _build_ingredient_inputs(
        self,
        recipes: list[RecipeORM],
    ) -> list[IngredientInput]:
        """
        Convert recipes into engine DTO.
        """

        ingredients: list[IngredientInput] = []

        for recipe in recipes:

            for ingredient in recipe.ingredients:

                ingredients.append(
                    IngredientInput(
                        product_name=(
                            ingredient.product.name
                        ),
                        amount_per_person=(
                            ingredient.amount_per_person
                        ),
                        unit=(
                            ingredient.product.unit
                        ),
                    )
                )

        return ingredients

    def _collect_package_sizes(
        self,
        recipes: list[RecipeORM],
    ) -> dict[str, int]:
        """
        Collect product package sizes.
        """

        package_sizes: dict[str, int] = {}

        for recipe in recipes:

            for ingredient in recipe.ingredients:

                product = ingredient.product

                if product.package_size:
                    package_sizes[
                        product.name
                    ] = product.package_size

        return package_sizes