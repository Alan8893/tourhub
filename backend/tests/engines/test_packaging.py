from app.engines.packaging import (
    PackagingInput,
    calculate_packages,
)


def test_calculate_packages():

    result = calculate_packages(
        items=[
            PackagingInput(
                product_name="Рис",
                amount=6000,
                unit="gram",
                package_size=900,
            )
        ]
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.product_name == "Рис"

    assert item.amount == 6000

    assert item.package_size == 900

    assert item.packages == 7