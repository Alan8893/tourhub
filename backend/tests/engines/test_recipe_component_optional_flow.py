from app.engines.shopping_list import IngredientInput, calculate_shopping_list


def test_optional_components_are_hidden_by_default():
    result = calculate_shopping_list(
        people=5,
        days=1,
        ingredients=[
            IngredientInput(
                product_name="Lemon",
                amount_per_person=1,
                unit="piece",
                component_type="optional",
            )
        ],
    )

    assert result.items == []


def test_optional_components_can_be_requested():
    result = calculate_shopping_list(
        people=5,
        days=1,
        ingredients=[
            IngredientInput(
                product_name="Lemon",
                amount_per_person=1,
                unit="piece",
                component_type="serving_add_on",
            )
        ],
        include_optional=True,
    )

    assert result.items[0].product_name == "Lemon"
    assert result.items[0].amount == 5
