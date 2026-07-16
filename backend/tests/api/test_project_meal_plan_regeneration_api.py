from uuid import NAMESPACE_URL, uuid5

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


OATMEAL_ID = "10000000-0000-0000-0000-000000000001"
APPLE_ID = "10000000-0000-0000-0000-000000000002"
SOUP_ID = "10000000-0000-0000-0000-000000000003"
MANUAL_ID = "10000000-0000-0000-0000-000000000004"


def _classified_dish(
    dish_id: str,
    name: str,
    role: str,
    meal_type: str,
) -> tuple[RecipeORM, DishORM]:
    recipe = RecipeORM(id=str(uuid5(NAMESPACE_URL, f"recipe:{dish_id}")), name=f"{name} recipe")
    dish = DishORM(id=dish_id, name=name, recipe=recipe)
    assignment = DishMealRoleORM(
        dish=dish,
        role=role,
        is_repeatable=False,
    )
    assignment.meal_types = [
        DishMealRoleMealTypeORM(
            dish_id=dish_id,
            role=role,
            meal_type=meal_type,
        )
    ]
    return recipe, dish


def test_project_regeneration_preserves_manual_and_empty_slots(client, db_session):
    project = ProjectORM(
        id=41,
        name="Manual regeneration",
        participants=6,
        days=1,
        first_meal="breakfast",
        last_meal="lunch",
        status="draft",
    )
    classified = [
        _classified_dish(OATMEAL_ID, "Oatmeal", "main", "breakfast"),
        _classified_dish(APPLE_ID, "Apple", "snack", "snack"),
        _classified_dish(SOUP_ID, "Soup", "main", "lunch"),
    ]
    manual_recipe = RecipeORM(
        id=str(uuid5(NAMESPACE_URL, "recipe:manual-regeneration")),
        name="Manual recipe",
    )
    manual_dish = DishORM(id=MANUAL_ID, name="Manual unclassified dish", recipe=manual_recipe)
    db_session.add(project)
    for recipe, dish in classified:
        db_session.add_all([recipe, dish])
    db_session.add_all([manual_recipe, manual_dish])
    db_session.commit()

    initial_response = client.post("/api/v1/meal-plans/project/41/generate")

    assert initial_response.status_code == 200
    initial = initial_response.json()
    assert initial["warnings"] == []
    initial_slots = {meal["meal_type"]: meal for meal in initial["meals"]}

    breakfast = initial_slots["breakfast"]
    replace_response = client.put(
        f"/api/v1/meal-slots/{breakfast['id']}/dishes/"
        f"{breakfast['dishes'][0]['id']}/{MANUAL_ID}"
    )
    assert replace_response.status_code == 200

    snack = initial_slots["snack"]
    remove_response = client.delete(
        f"/api/v1/meal-slots/{snack['id']}/dishes/{snack['dishes'][0]['id']}"
    )
    assert remove_response.status_code == 200

    regenerated_response = client.post("/api/v1/meal-plans/project/41/generate")

    assert regenerated_response.status_code == 200
    regenerated = regenerated_response.json()
    assert regenerated["id"] == initial["id"]
    assert regenerated["warnings"] == []
    regenerated_slots = {meal["meal_type"]: meal for meal in regenerated["meals"]}
    assert [dish["dish_id"] for dish in regenerated_slots["breakfast"]["dishes"]] == [
        MANUAL_ID
    ]
    assert regenerated_slots["snack"]["dishes"] == []
    assert [dish["dish_id"] for dish in regenerated_slots["lunch"]["dishes"]] == [SOUP_ID]
    assert db_session.query(MealPlanORM).filter(MealPlanORM.project_id == 41).count() == 1

    stored_response = client.get("/api/v1/meal-plans/project/41")
    assert stored_response.status_code == 200
    stored_slots = {
        meal["meal_type"]: meal
        for meal in stored_response.json()["meals"]
    }
    assert [dish["dish_id"] for dish in stored_slots["breakfast"]["dishes"]] == [
        MANUAL_ID
    ]
    assert stored_slots["snack"]["dishes"] == []
