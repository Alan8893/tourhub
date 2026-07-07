from uuid import uuid4

from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.services.purchase_checklist_service import PurchaseChecklistService


def test_purchase_checklist_progress(db_session):
    checklist = PurchaseChecklistORM(
        id=str(uuid4()),
        meal_plan_id="meal-plan-1",
        status="in_progress",
    )
    db_session.add(checklist)
    db_session.flush()

    db_session.add_all(
        [
            PurchaseChecklistItemORM(
                id=str(uuid4()),
                checklist=checklist,
                product_id="product-1",
                required_quantity=100,
                purchased_quantity=100,
                unit="gram",
                is_checked=True,
            ),
            PurchaseChecklistItemORM(
                id=str(uuid4()),
                checklist=checklist,
                product_id="product-2",
                required_quantity=200,
                purchased_quantity=0,
                unit="gram",
                is_checked=False,
            ),
        ]
    )
    db_session.commit()

    service = PurchaseChecklistService(
        PurchaseChecklistRepository(db_session)
    )

    progress = service.get_progress(checklist.id)

    assert progress["status"] == "in_progress"
    assert progress["total_items"] == 2
    assert progress["checked_items"] == 1
    assert progress["progress_percent"] == 50
