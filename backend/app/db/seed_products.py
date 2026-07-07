from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.product import ProductORM


PRODUCTS = [
    {
        "name": "Гречка",
        "category": "cereal",
        "unit": "gram",
        "package_size": 900,
    },
    {
        "name": "Рис",
        "category": "cereal",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Макароны",
        "category": "pasta",
        "unit": "gram",
        "package_size": 500,
    },
    {
        "name": "Картофель",
        "category": "vegetable",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Лук",
        "category": "vegetable",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Морковь",
        "category": "vegetable",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Мясо",
        "category": "protein",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Тушёнка",
        "category": "protein",
        "unit": "gram",
        "package_size": 338,
    },
    {
        "name": "Масло",
        "category": "fat",
        "unit": "gram",
        "package_size": 200,
    },
    {
        "name": "Сахар",
        "category": "sweetener",
        "unit": "gram",
        "package_size": 1000,
    },
    {
        "name": "Чай",
        "category": "drink",
        "unit": "gram",
        "package_size": 100,
    },
]


def seed_products(session: Session) -> None:
    """
    Create base products.

    The function is idempotent:
    running it multiple times does not create duplicates.
    """

    for product_data in PRODUCTS:
        exists = (
            session.query(ProductORM)
            .filter(
                ProductORM.name == product_data["name"]
            )
            .first()
        )

        if exists:
            continue

        product = ProductORM(
            id=str(uuid4()),
            **product_data,
        )

        session.add(product)

    session.commit()