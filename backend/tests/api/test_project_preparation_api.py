from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_list import PurchaseListORM
from app.models.meal_plan import MealPlanORM
from app.modules.projects.models.project import ProjectORM



def test_prepare_project_not_found(client):
    response = client.post("/api/v1/projects/999/prepare")

    assert response.status_code == 404



def test_prepare_project_requires_meal_plan(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    db_session.add(project)
    db_session.commit()

    response = client.post("/api/v1/projects/1/prepare")

    assert response.status_code == 404
