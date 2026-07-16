from uuid import NAMESPACE_URL, uuid5

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


DISH_ID = "20000000-0000-0000-0000-000000000001"


def _breakfast_main() -> tuple[RecipeORM, DishORM]:
    recipe = RecipeORM(
        id=str(uuid5(NAMESPACE_URL, "recipe:warning-persistence-breakfast")),
        name="Breakfast recipe",
    )
    dish = DishORM(id=DISH_ID, name="Breakfast main", recipe=recipe)
    assignment = DishMealRoleORM(
        dish=dish,
        role="main",
        is_repeatable=False,
    )
    assignment.meal_types = [
        DishMealRoleMealTypeORM(
            dish_id=dish.id,
            role="main",
            meal_type="breakfast",
        )
    ]
    return recipe, dish


def test_generation_warnings_persist_until_next_regeneration(client, db_session):
    project = ProjectORM(
        id=51,
        name="Warning persistence",
        participants=4,
        days=1,
        first_meal="breakfast",
        last_meal="breakfast",
        status="draft",
    )
    db_session.add(project)
    db_session.commit()

    generated_response = client.post("/api/v1/meal-plans/project/51/generate")

    assert generated_response.status_code == 200
    expected_warnings = ["No main dishes available for breakfast"]
    assert generated_response.json()["warnings"] == expected_warnings

    stored_response = client.get("/api/v1/meal-plans/project/51")

    assert stored_response.status_code == 200
    assert stored_response.json()["warnings"] == expected_warnings

    recipe, dish = _breakfast_main()
    db_session.add_all([recipe, dish])
    db_session.commit()

    unchanged_response = client.get("/api/v1/meal-plans/project/51")

    assert unchanged_response.status_code == 200
    assert unchanged_response.json()["warnings"] == expected_warnings

    regenerated_response = client.post("/api/v1/meal-plans/project/51/generate")

    assert regenerated_response.status_code == 200
    assert regenerated_response.json()["warnings"] == []

    refreshed_response = client.get("/api/v1/meal-plans/project/51")

    assert refreshed_response.status_code == 200
    assert refreshed_response.json()["warnings"] == []
