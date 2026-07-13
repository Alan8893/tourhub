from app.engines.packaging import PackagingInput, calculate_packages


def test_recipe_component_package_calculation():
    result = calculate_packages(
        [
            PackagingInput(
                product_name="Buckwheat",
                amount=6000,
                unit="gram",
                package_size=900,
            )
        ]
    )

    assert result.items[0].product_name == "Buckwheat"
    assert result.items[0].packages == 7


def test_recipe_component_single_package_case():
    result = calculate_packages(
        [
            PackagingInput(
                product_name="Beans",
                amount=1,
                unit="can",
                package_size=1,
            )
        ]
    )

    assert result.items[0].packages == 1
