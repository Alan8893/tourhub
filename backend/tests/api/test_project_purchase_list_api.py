from app.models.purchase_list import PurchaseListORM
from app.modules.projects.models.project import ProjectORM


PURCHASE_LIST_ID = "8f2f5c6d-6b8f-4db2-9e1a-8c9e6d5a1111"


def test_get_project_purchase_list(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    purchase_list = PurchaseListORM(
        id=PURCHASE_LIST_ID,
        project_id=1,
        meal_plan_id="ea557e05-d89b-4403-9822-5bc3a95c8f2c",
        status="prepared",
    )

    db_session.add(project)
    db_session.add(purchase_list)
    db_session.commit()

    response = client.get(
        "/api/v1/purchase-lists/project/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == 1
    assert data["meal_plan_id"] == "ea557e05-d89b-4403-9822-5bc3a95c8f2c"


def test_get_project_purchase_list_not_found(client):
    response = client.get(
        "/api/v1/purchase-lists/project/999"
    )

    assert response.status_code == 404
