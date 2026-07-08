from app.models.purchase_checklist import PurchaseChecklistORM
from app.modules.projects.models.project import ProjectORM


CHECKLIST_ID = "7f7f5c6d-6b8f-4db2-9e1a-8c9e6d5a2222"


def test_get_project_purchase_checklist(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    checklist = PurchaseChecklistORM(
        id=CHECKLIST_ID,
        project_id=1,
        meal_plan_id="ea557e05-d89b-4403-9822-5bc3a95c8f2c",
        status="draft",
    )

    db_session.add(project)
    db_session.add(checklist)
    db_session.commit()

    response = client.get(
        "/api/v1/purchase-checklists/project/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == 1
    assert data["meal_plan_id"] == "ea557e05-d89b-4403-9822-5bc3a95c8f2c"


def test_get_project_purchase_checklist_not_found(client):
    response = client.get(
        "/api/v1/purchase-checklists/project/999"
    )

    assert response.status_code == 404
