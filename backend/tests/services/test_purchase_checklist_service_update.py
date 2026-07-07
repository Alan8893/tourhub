from uuid import uuid4

from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.product import ProductORM
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.services.purchase_checklist_service import PurchaseChecklistService


def test_update_item_marks_checklist_completed(db_session):
    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )

    checklist = PurchaseChecklistORM(
        id=str(uuid4()),
        meal_plan_id="meal-plan-1",
        status="draft",
    )

    item = PurchaseChecklistItemORM(
        id=str(uuid4()),
        checklist=checklist,
        product_id=product.id,
        required_quantity=500,
        purchased_quantity=0,
        unit="gram",
        is_checked=False,
    )

    db_session.add_all([product, checklist, item])
    db_session.commit()

    service = PurchaseChecklistService(
        PurchaseChecklistRepository(db_session)
    )

    updated = service.update_item(
        item.id,
        checked=True,
        purchased_quantity=500,
    )

    assert updated.is_checked is True
    assert updated.purchased_quantity == 500
    assert updated.checklist.status == "completed"
