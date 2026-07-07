from app.engines.shopping_list import (
    IngredientInput,
    calculate_shopping_list,
)


def test_shopping_list_aggregates_same_products():
    result = calculate_shopping_list(
        people=5,
        days=2,
        ingredients=[
            IngredientInput(
                product_name="Rice",
                amount_per_person=100,
                unit="g",
            ),
            IngredientInput(
                product_name="Rice",
                amount_per_person=100,
                unit="g",
            ),
        ],
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.product_name == "Rice"
    assert item.quantity == 2000
    assert item.unit == "g"