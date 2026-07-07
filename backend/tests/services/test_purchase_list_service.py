from uuid import uuid4

from app.models.product import ProductORM
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.purchase_list_service import PurchaseListService


class FakePackagingItem:
    product_name = "Рис"
    amount = 2000
    unit = "gram"
    package_size = 1000
    packages = 2


class FakePackagingResult:
    items = [FakePackagingItem()]


def test_create_purchase_list_from_packaged_shopping(db_session):
    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )

    db_session.add(product)
    db_session.commit()

    service = PurchaseListService(
        PurchaseListRepository(db_session)
    )

    purchase_list = service.create_from_packaged_shopping(
        meal_plan_id="meal-plan-1",
        shopping_result=FakePackagingResult(),
    )

    assert purchase_list.status == "prepared"
    assert len(purchase_list.items) == 1
    assert purchase_list.items[0].product_id == product.id
    assert purchase_list.items[0].packages_count == 2
