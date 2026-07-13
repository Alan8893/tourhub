from app.engines.shopping_list import (
    IngredientInput,
    calculate_shopping_list,
)


def test_recipe_component_per_person_calculation():
    result = calculate_shopping_list(
        people=10,
        days=1,
        ingredients=[
            IngredientInput(
                product_name="Rice",
                amount_per_person=120,
                unit="gram",
            )
        ],
    )

    assert result.items[0].product_name == "Rice"
    assert result.items[0].amount == 1200


def test_recipe_component_package_per_people_calculation():
    result = calculate_shopping_list(
        people=10,
        days=1,
        ingredients=[
            IngredientInput(
                product_name="Beans can",
                amount_per_person=1,
                unit="can",
                calculation_type="package_per_people",
                people_count=4,
            )
        ],
    )

    assert result.items[0].amount == 3
