from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class IngredientInput:
    """
    Ingredient required for calculation.

    amount_per_person:
        quantity required for one person.

    unit:
        measurement unit (g, kg, ml, l, pcs, etc.)
    """

    product_name: str
    amount_per_person: float
    unit: str


@dataclass(frozen=True)
class ShoppingListItem:
    product_name: str
    amount: float
    unit: str

    @property
    def quantity(self) -> float:
        """
        Backward compatible alias.
        """
        return self.amount


@dataclass(frozen=True)
class ShoppingListResult:
    items: list[ShoppingListItem]


def aggregate_products(
    items: list[ShoppingListItem],
) -> list[ShoppingListItem]:
    """
    Merge products with the same name and unit.

    Example:

    Rice 500 g
    Rice 500 g

    becomes:

    Rice 1000 g
    """

    aggregated: OrderedDict[
        tuple[str, str],
        float,
    ] = OrderedDict()

    for item in items:
        key = (
            item.product_name,
            item.unit,
        )

        aggregated[key] = (
            aggregated.get(key, 0)
            + item.quantity
        )

    return [
        ShoppingListItem(
            product_name=product_name,
            amount=quantity,
            unit=unit,
        )
        for (
            product_name,
            unit,
        ), quantity in aggregated.items()
    ]


def calculate_shopping_list(
    people: int,
    days: int,
    ingredients: list[IngredientInput],
) -> ShoppingListResult:
    """
    Calculate total products required
    for a hiking group.
    """

    calculated_items: list[ShoppingListItem] = []

    multiplier = people * days

    for ingredient in ingredients:

        calculated_items.append(
            ShoppingListItem(
                product_name=ingredient.product_name,
                amount=(
                    ingredient.amount_per_person
                    * multiplier
                ),
                unit=ingredient.unit,
            )
        )

    return ShoppingListResult(
        items=aggregate_products(
            calculated_items
        )
    )