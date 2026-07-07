from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.engines.shopping_list import (
    ShoppingListItem,
    ShoppingListResult,
)
from app.models.product import ProductORM
from app.repositories.purchase_checklist_repository import (
    PurchaseChecklistRepository,
)
from app.services.purchase_checklist_service import (
    PurchaseChecklistService,
)


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={
        "check_same_thread": False,
    },
)

TestingSessionLocal = sessionmaker(
    bind=engine,
)


def setup_database():
    Base.metadata.create_all(
        bind=engine,
    )


def test_create_purchase_checklist_from_shopping_list():
    setup_database()

    session = TestingSessionLocal()

    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )

    session.add(product)
    session.commit()

    repository = PurchaseChecklistRepository(
        session,
    )

    service = PurchaseChecklistService(
        repository,
    )

    shopping_list = ShoppingListResult(
        items=[
            ShoppingListItem(
                product_name="Рис",
                amount=500,
                unit="gram",
            )
        ]
    )

    checklist = service.create_from_shopping_list(
        meal_plan_id="meal-plan-1",
        shopping_list=shopping_list,
    )

    assert checklist.status == "draft"
    assert len(checklist.items) == 1
    assert checklist.items[0].product_id == product.id
    assert checklist.items[0].required_quantity == 500

    session.close()


def test_create_purchase_checklist_product_not_found():
    setup_database()

    session = TestingSessionLocal()

    repository = PurchaseChecklistRepository(
        session,
    )

    service = PurchaseChecklistService(
        repository,
    )

    shopping_list = ShoppingListResult(
        items=[
            ShoppingListItem(
                product_name="Несуществующий продукт",
                amount=100,
                unit="gram",
            )
        ]
    )

    try:
        service.create_from_shopping_list(
            meal_plan_id="meal-plan-1",
            shopping_list=shopping_list,
        )
        assert False
    except ValueError as error:
        assert "Product not found" in str(error)

    session.close()
