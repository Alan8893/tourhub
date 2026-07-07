from app.engines.shopping_list import (
    IngredientInput,
    calculate_shopping_list,
)


def test_calculate_shopping_list():
    ingredients = [
        IngredientInput(
            product_name="Рис",
            amount_per_person=120,
            unit="gram",
        )
    ]

    result = calculate_shopping_list(
        people=10,
        days=5,
        ingredients=ingredients,
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.product_name == "Рис"
    assert item.amount == 6000
    assert item.unit == "gram"


def test_calculate_multiple_products():
    ingredients = [
        IngredientInput(
            product_name="Рис",
            amount_per_person=120,
            unit="gram",
        ),
        IngredientInput(
            product_name="Мясо",
            amount_per_person=100,
            unit="gram",
        ),
    ]

    result = calculate_shopping_list(
        people=5,
        days=3,
        ingredients=ingredients,
    )

    assert result.items[0].amount == 1800
    assert result.items[1].amount == 1500


def test_invalid_people_count():

    ingredients = [
        IngredientInput(
            product_name="Рис",
            amount_per_person=120,
            unit="gram",
        )
    ]

    try:
        calculate_shopping_list(
            people=0,
            days=5,
            ingredients=ingredients,
        )

        assert False

    except ValueError as error:
        assert str(error) == (
            "People must be greater than zero"
        )