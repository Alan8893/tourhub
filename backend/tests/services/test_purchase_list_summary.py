from uuid import uuid4

from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.purchase_list_service import PurchaseListService


def test_purchase_list_summary(db_session):
    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )
    db_session.add(product)
    db_session.commit()

    purchase_list = PurchaseListORM(
        id=str(uuid4()),
        meal_plan_id="meal-plan-1",
        status="prepared",
    )
    db_session.add(purchase_list)
    db_session.flush()

    db_session.add(
        PurchaseListItemORM(
            id=str(uuid4()),
            purchase_list=purchase_list,
            product_id=product.id,
            required_quantity=2000,
            required_unit="gram",
            package_size=1000,
            package_unit="gram",
            packages_count=2,
        )
    )
    db_session.commit()

    service = PurchaseListService(PurchaseListRepository(db_session))

    summary = service.get_summary(purchase_list.id)

    assert summary["status"] == "prepared"
    assert summary["items_total"] == 1
    assert summary["packages_total"] == 2
