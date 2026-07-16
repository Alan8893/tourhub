from app.models.meal_plan import MealPlanORM
from app.models.product import ProductORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.modules.projects.models.project import ProjectORM


MEAL_PLAN_ID = "40000000-0000-0000-0000-000000000001"
CHECKLIST_ID = "40000000-0000-0000-0000-000000000002"
ITEM_ID = "40000000-0000-0000-0000-000000000003"
PRODUCT_ID = "40000000-0000-0000-0000-000000000004"


def test_project_checklist_exposes_and_updates_purchase_quantities(client, db_session):
    project = ProjectORM(
        id=71,
        name="Purchase quantities",
        participants=4,
        days=1,
        status="draft",
    )
    meal_plan = MealPlanORM(
        id=MEAL_PLAN_ID,
        project_id=project.id,
        name=project.name,
        participants=project.participants,
        days_count=project.days,
    )
    product = ProductORM(
        id=PRODUCT_ID,
        name="Гречка",
        category="cereal",
        unit="gram",
        package_size=800,
    )
    checklist = PurchaseChecklistORM(
        id=CHECKLIST_ID,
        project_id=project.id,
        meal_plan_id=meal_plan.id,
        status="draft",
    )
    item = PurchaseChecklistItemORM(
        id=ITEM_ID,
        checklist=checklist,
        product=product,
        required_quantity=500,
        purchased_quantity=100,
        unit="gram",
        is_checked=False,
    )
    db_session.add_all([project, meal_plan, product, checklist, item])
    db_session.commit()

    initial_response = client.get("/api/v1/purchase-checklists/project/71")

    assert initial_response.status_code == 200
    initial_item = initial_response.json()["items"][0]
    assert initial_item == {
        "id": ITEM_ID,
        "product_id": PRODUCT_ID,
        "product_name": "Гречка",
        "required_quantity": 500.0,
        "purchased_quantity": 100.0,
        "remaining_quantity": 400.0,
        "unit": "gram",
        "is_checked": False,
    }

    update_response = client.patch(
        f"/api/v1/purchase-checklists/items/{ITEM_ID}",
        json={"purchased_quantity": 600, "is_checked": True},
    )

    assert update_response.status_code == 200
    assert update_response.json()["purchased_quantity"] == 600.0
    assert update_response.json()["remaining_quantity"] == 0.0
    assert update_response.json()["is_checked"] is True

    stored_response = client.get("/api/v1/purchase-checklists/project/71")
    assert stored_response.status_code == 200
    assert stored_response.json()["status"] == "completed"
    assert stored_response.json()["items"][0]["remaining_quantity"] == 0.0

    invalid_response = client.patch(
        f"/api/v1/purchase-checklists/items/{ITEM_ID}",
        json={"purchased_quantity": -1},
    )
    assert invalid_response.status_code == 422
