from app.engines.shopping_list import (
    IngredientInput,
    calculate_shopping_list,
)



def test_package_per_people_calculation():
    result = calculate_shopping_list(
        people=10,
        days=1,
        ingredients=[
            IngredientInput(
                product_name="Beans",
                amount_per_person=1,
                unit="can",
                calculation_type="package_per_people",
                people_count=4,
            )
        ],
    )

    assert len(result.items) == 1
    assert result.items[0].quantity == 3



def test_fixed_group_calculation():
    result = calculate_shopping_list(
        people=10,
        days=3,
        ingredients=[
            IngredientInput(
                product_name="Salt",
                amount_per_person=1,
                unit="pack",
                calculation_type="fixed_group",
            )
        ],
    )

    assert result.items[0].quantity == 3



def test_recipe_component_default_keeps_per_person_behavior():
    result = calculate_shopping_list(
        people=5,
        days=2,
        ingredients=[
            IngredientInput(
                product_name="Rice",
                amount_per_person=100,
                unit="g",
            )
        ],
    )

    assert result.items[0].quantity == 1000
