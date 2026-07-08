from app.models.meal_plan import MealPlanORM
from app.modules.projects.models.project import ProjectORM


def test_get_project_meal_plan_endpoint(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    meal_plan = MealPlanORM(
        id="test-meal-plan-1",
        project_id=1,
        name="Altai Trip 2026",
        participants=10,
        days_count=7,
    )

    db_session.add(project)
    db_session.add(meal_plan)
    db_session.commit()

    response = client.get(
        "/api/v1/meal-plans/project/1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["project_id"] == 1
    assert data["name"] == "Altai Trip 2026"
    assert data["participants"] == 10
    assert data["days_count"] == 7


def test_get_project_meal_plan_not_found(client):
    response = client.get(
        "/api/v1/meal-plans/project/999"
    )

    assert response.status_code == 404
