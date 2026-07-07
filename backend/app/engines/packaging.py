from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class PackagingInput:
    """
    Product quantity required
    with package information.
    """

    product_name: str

    amount: float

    unit: str

    package_size: float


@dataclass(frozen=True)
class PackagedShoppingItem:
    """
    Product purchase information.
    """

    product_name: str

    amount: float

    unit: str

    package_size: float

    packages: int


@dataclass(frozen=True)
class PackagedShoppingResult:
    """
    Shopping list with package calculation.
    """

    items: list[PackagedShoppingItem]


def calculate_packages(
    items: list[PackagingInput],
) -> PackagedShoppingResult:
    """
    Calculate number of packages required.

    Example:

    6000 grams required

    package size:
    900 grams

    result:
    7 packages
    """

    result: list[PackagedShoppingItem] = []

    for item in items:

        if item.package_size <= 0:
            raise ValueError(
                "Package size must be greater than zero"
            )

        packages = ceil(
            item.amount / item.package_size
        )

        result.append(
            PackagedShoppingItem(
                product_name=item.product_name,
                amount=item.amount,
                unit=item.unit,
                package_size=item.package_size,
                packages=packages,
            )
        )

    return PackagedShoppingResult(
        items=result
    )