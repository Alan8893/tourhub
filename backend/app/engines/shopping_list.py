from dataclasses import dataclass


@dataclass(frozen=True)
class IngredientInput:
    """
    Ingredient consumption rule.

    Example:
    Rice = 120 gram/person
    """

    product_name: str
    amount_per_person: int
    unit: str


@dataclass(frozen=True)
class ShoppingItem:
    """
    Calculated shopping item.
    """

    product_name: str
    amount: int
    unit: str


@dataclass(frozen=True)
class ShoppingListResult:
    items: list[ShoppingItem]


def calculate_shopping_list(
    people: int,
    days: int,
    ingredients: list[IngredientInput],
) -> ShoppingListResult:
    """
    Calculate total products required.

    Formula:

    amount_per_person × people × days
    """

    if people <= 0:
        raise ValueError(
            "People must be greater than zero"
        )

    if days <= 0:
        raise ValueError(
            "Days must be greater than zero"
        )

    items = []

    for ingredient in ingredients:
        total_amount = (
            ingredient.amount_per_person
            * people
            * days
        )

        items.append(
            ShoppingItem(
                product_name=ingredient.product_name,
                amount=total_amount,
                unit=ingredient.unit,
            )
        )

    return ShoppingListResult(
        items=items
    )