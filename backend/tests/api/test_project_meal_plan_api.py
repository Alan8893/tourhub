from app.models.meal_plan import MealPlanORM
from app.modules.projects.models.project import ProjectORM


MEAL_PLAN_ID = "ea557e05-d89b-4403-9822-5bc3a95c8f2c"


def test_get_project_meal_plan_endpoint(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    meal_plan = MealPlanORM(
        id=MEAL_PLAN_ID,
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

    for meal in data["meals"]:
        assert "id" in meal
