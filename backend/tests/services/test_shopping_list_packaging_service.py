from uuid import uuid4

from app.models.base import Base
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.ingredient import IngredientORM

from app.services.shopping_list_service import (
    ShoppingListService,
)

from tests.conftest import (
    TestingSessionLocal,
    setup_database,
    test_engine,
)


def test_shopping_list_service_calculates_packages():

    setup_database()

    session = TestingSessionLocal()

    try:
        product = ProductORM(
            id=str(uuid4()),
            name="Рис для упаковки",
            category="cereal",
            unit="gram",
            package_size=900,
        )

        recipe = RecipeORM(
            id=str(uuid4()),
            name="Тестовый плов упаковка",
        )

        ingredient = IngredientORM(
            id=str(uuid4()),
            recipe_id=recipe.id,
            product_id=product.id,
            amount_per_person=120,
        )

        session.add(product)
        session.add(recipe)
        session.add(ingredient)

        session.commit()

        service = ShoppingListService(
            session
        )

        result = service.calculate_packaged_for_recipes(
            recipes=[
                recipe,
            ],
            people=10,
            days=5,
        )

        assert len(result.items) == 1

        item = result.items[0]

        assert item.product_name == "Рис для упаковки"

        assert item.amount == 6000

        assert item.package_size == 900

        assert item.packages == 7

    finally:
        session.close()

        Base.metadata.drop_all(
            bind=test_engine
        )