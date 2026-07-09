from collections import OrderedDict
from dataclasses import dataclass


@dataclass(frozen=True)
class IngredientInput:
    """
    Product required for shopping calculation.

    Supports legacy per-person calculation and
    recipe component based rules.
    """

    product_name: str
    amount_per_person: float
    unit: str
    calculation_type: str = "per_person"
    people_count: int | None = None


@dataclass(frozen=True)
class ShoppingListItem:
    product_name: str
    amount: float
    unit: str

    @property
    def quantity(self) -> float:
        return self.amount


@dataclass(frozen=True)
class ShoppingListResult:
    items: list[ShoppingListItem]


def aggregate_products(
    items: list[ShoppingListItem],
) -> list[ShoppingListItem]:
    aggregated: OrderedDict[tuple[str, str], float] = OrderedDict()

    for item in items:
        key = (item.product_name, item.unit)
        aggregated[key] = aggregated.get(key, 0) + item.quantity

    return [
        ShoppingListItem(
            product_name=product_name,
            amount=quantity,
            unit=unit,
        )
        for (product_name, unit), quantity in aggregated.items()
    ]


def _calculate_amount(
    ingredient: IngredientInput,
    people: int,
    days: int,
) -> float:
    """
    Calculate amount according to component rule.

    Supported modes:
    - per_person: amount * people * days
    - fixed_group: amount * days
    - package_per_people: ceil(people / people_count) * amount * days
    """

    if ingredient.calculation_type == "fixed_group":
        return ingredient.amount_per_person * days

    if ingredient.calculation_type == "package_per_people":
        if not ingredient.people_count:
            raise ValueError(
                "people_count is required for package_per_people"
            )

        packages = -(-people // ingredient.people_count)
        return ingredient.amount_per_person * packages * days

    return ingredient.amount_per_person * people * days


def calculate_shopping_list(
    people: int,
    days: int,
    ingredients: list[IngredientInput],
) -> ShoppingListResult:
    calculated_items: list[ShoppingListItem] = []

    for ingredient in ingredients:
        calculated_items.append(
            ShoppingListItem(
                product_name=ingredient.product_name,
                amount=_calculate_amount(
                    ingredient,
                    people,
                    days,
                ),
                unit=ingredient.unit,
            )
        )

    return ShoppingListResult(
        items=aggregate_products(calculated_items)
    )
