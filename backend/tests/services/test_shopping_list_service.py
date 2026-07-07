from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.ingredient import IngredientORM
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.services.shopping_list_service import ShoppingListService


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={
        "check_same_thread": False
    },
)

TestingSessionLocal = sessionmaker(
    bind=engine
)


def setup_database():
    Base.metadata.create_all(
        bind=engine
    )


def test_shopping_list_service():

    setup_database()

    session = TestingSessionLocal()

    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )

    recipe = RecipeORM(
        id=str(uuid4()),
        name="Тестовый плов",
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

    result = service.calculate_for_recipe(
        recipe_id=recipe.id,
        people=10,
        days=5,
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.product_name == "Рис"
    assert item.amount == 6000
    assert item.unit == "gram"

    session.close()