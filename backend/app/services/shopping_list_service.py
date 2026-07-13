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

    Uses RecipeComponent as the primary recipe source.
    Falls back to legacy Ingredient for backward compatibility.
    """

    def __init__(self, session: Session):
        self.session = session

    def calculate_for_recipe(
        self,
        recipe_id: str,
        people: int,
        days: int,
        include_optional: bool = False,
    ) -> ShoppingListResult:
        recipe = (
            self.session.query(RecipeORM)
            .filter(RecipeORM.id == recipe_id)
            .first()
        )

        if not recipe:
            raise ValueError(f"Recipe not found: {recipe_id}")

        return self.calculate_for_recipes(
            [recipe],
            people,
            days,
            include_optional=include_optional,
        )

    def calculate_for_recipes(
        self,
        recipes: list[RecipeORM],
        people: int,
        days: int,
        include_optional: bool = False,
    ) -> ShoppingListResult:
        return calculate_shopping_list(
            people=people,
            days=days,
            ingredients=self._build_ingredient_inputs(recipes),
            include_optional=include_optional,
        )

    def calculate_packaged_for_recipes(
        self,
        recipes: list[RecipeORM],
        people: int,
        days: int,
    ) -> PackagedShoppingResult:
        base_result = calculate_shopping_list(
            people=people,
            days=days,
            ingredients=self._build_ingredient_inputs(recipes),
        )

        packaging_inputs: list[PackagingInput] = []
        package_sizes = self._collect_package_sizes(recipes)

        for item in base_result.items:
            package_size = package_sizes.get(item.product_name)
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

        return calculate_packages(packaging_inputs)

    def _build_ingredient_inputs(
        self,
        recipes: list[RecipeORM],
    ) -> list[IngredientInput]:
        inputs: list[IngredientInput] = []

        for recipe in recipes:
            if recipe.components:
                for component in recipe.components:
                    inputs.append(
                        IngredientInput(
                            product_name=component.product.name,
                            amount_per_person=component.amount,
                            unit=component.unit,
                            calculation_type=component.calculation_type,
                            people_count=component.people_count,
                            component_type=component.component_type,
                        )
                    )
                continue

            for ingredient in recipe.ingredients:
                inputs.append(
                    IngredientInput(
                        product_name=ingredient.product.name,
                        amount_per_person=ingredient.amount_per_person,
                        unit=ingredient.product.unit,
                    )
                )

        return inputs

    def _collect_package_sizes(
        self,
        recipes: list[RecipeORM],
    ) -> dict[str, int]:
        package_sizes: dict[str, int] = {}

        for recipe in recipes:
            source = recipe.components if recipe.components else []

            for component in source:
                if component.product.package_size:
                    package_sizes[component.product.name] = component.product.package_size

            if not source:
                for ingredient in recipe.ingredients:
                    if ingredient.product.package_size:
                        package_sizes[ingredient.product.name] = ingredient.product.package_size

        return package_sizes
