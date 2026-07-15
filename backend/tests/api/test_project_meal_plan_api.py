from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


MEAL_PLAN_ID = "ea557e05-d89b-4403-9822-5bc3a95c8f2c"
DISH_ID = "550e8400-e29b-41d4-a716-446655440001"
RECIPE_ID = "660e8400-e29b-41d4-a716-446655440001"


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

    response = client.get("/api/v1/meal-plans/project/1")

    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == 1
    assert data["name"] == "Altai Trip 2026"
    assert data["participants"] == 10
    assert data["days_count"] == 7
    for meal in data["meals"]:
        assert "id" in meal


def test_generate_project_meal_plan_exposes_catalogue_warning_and_relation_ids(
    client,
    db_session,
):
    project = ProjectORM(
        id=2,
        name="Short Catalogue",
        participants=4,
        days=1,
        first_meal="breakfast",
        last_meal="dinner",
        status="draft",
    )
    recipe = RecipeORM(id=RECIPE_ID, name="Only recipe")
    dish = DishORM(id=DISH_ID, name="Only dish", recipe=recipe)
    db_session.add_all([project, recipe, dish])
    db_session.commit()

    response = client.post("/api/v1/meal-plans/project/2/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["warnings"] == ["Dish database is insufficient"]
    assert [meal["meal_type"] for meal in data["meals"]] == [
        "breakfast",
        "snack",
        "lunch",
        "dinner",
    ]
    assert all(meal["dishes"][0]["id"] for meal in data["meals"])
    assert len(data["items"]) == 4
