from decimal import Decimal
from uuid import uuid4

from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.purchase_list_service import PurchaseListService


def test_create_document_dto(db_session):
    product = ProductORM(
        id=str(uuid4()),
        name="Rice",
        category="cereal",
        unit="gram",
        package_size=1000,
    )

    purchase_list = PurchaseListORM(
        id="purchase-1",
        meal_plan_id="meal-plan-1",
        status="prepared",
    )

    item = PurchaseListItemORM(
        id="item-1",
        purchase_list=purchase_list,
        product_id=product.id,
        required_quantity=Decimal("2000"),
        required_unit="gram",
        package_size=Decimal("1000"),
        package_unit="gram",
        packages_count=2,
    )

    db_session.add_all([
        product,
        purchase_list,
        item,
    ])
    db_session.commit()

    service = PurchaseListService(
        PurchaseListRepository(db_session)
    )

    result = service.create_document_dto(
        purchase_list
    )

    assert result.purchase_list_id == "purchase-1"
    assert result.items[0].product_name == "Rice"
    assert result.items[0].packages_count == 2
