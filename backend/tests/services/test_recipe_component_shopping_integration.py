from app.engines.shopping_list import IngredientInput, calculate_shopping_list


def test_recipe_component_optional_flow_reaches_shopping_engine():
    result = calculate_shopping_list(
        people=8,
        days=2,
        ingredients=[
            IngredientInput(
                product_name="Lemon",
                amount_per_person=1,
                unit="piece",
                component_type="serving_add_on",
            ),
            IngredientInput(
                product_name="Rice",
                amount_per_person=100,
                unit="gram",
                component_type="base",
            ),
        ],
        include_optional=False,
    )

    assert len(result.items) == 1
    assert result.items[0].product_name == "Rice"
