from uuid import NAMESPACE_URL, uuid5

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


MEAL_PLAN_ID = "ea557e05-d89b-4403-9822-5bc3a95c8f2c"
DISH_ID = "550e8400-e29b-41d4-a716-446655440001"
RECIPE_ID = "660e8400-e29b-41d4-a716-446655440001"
OATMEAL_ID = "00000000-0000-0000-0000-000000000101"
APPLE_ID = "00000000-0000-0000-0000-000000000102"
BORSCHT_ID = "00000000-0000-0000-0000-000000000103"
BUCKWHEAT_ID = "00000000-0000-0000-0000-000000000104"
BREAD_ID = "00000000-0000-0000-0000-000000000105"
TEA_ID = "00000000-0000-0000-0000-000000000106"


def _classified_dish(
    dish_id: str,
    name: str,
    role: str,
    meal_types: tuple[str, ...],
    *,
    is_repeatable: bool = False,
) -> tuple[RecipeORM, DishORM]:
    recipe = RecipeORM(id=str(uuid5(NAMESPACE_URL, f"recipe:{dish_id}")), name=f"{name} recipe")
    dish = DishORM(id=dish_id, name=name, recipe=recipe)
    assignment = DishMealRoleORM(
        dish=dish,
        role=role,
        is_repeatable=is_repeatable,
    )
    assignment.meal_types = [
        DishMealRoleMealTypeORM(
            dish_id=dish_id,
            role=role,
            meal_type=meal_type,
        )
        for meal_type in meal_types
    ]
    return recipe, dish


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
    assert data["warnings"] == [
        "No main dishes available for breakfast",
        "No snack dishes available for snack",
        "No main dishes available for lunch",
        "No main dishes available for dinner",
    ]
    assert [meal["meal_type"] for meal in data["meals"]] == [
        "breakfast",
        "snack",
        "lunch",
        "dinner",
    ]
    assert all(meal["id"] for meal in data["meals"])
    assert all(meal["dishes"] == [] for meal in data["meals"])
    assert data["items"] == []


def test_generate_project_meal_plan_uses_role_and_meal_type_compatibility(
    client,
    db_session,
):
    project = ProjectORM(
        id=3,
        name="Classified Catalogue",
        participants=6,
        days=1,
        first_meal="breakfast",
        last_meal="dinner",
        status="draft",
    )
    classified = [
        _classified_dish(OATMEAL_ID, "Овсяная каша", "main", ("breakfast",)),
        _classified_dish(APPLE_ID, "Яблоко", "snack", ("snack",)),
        _classified_dish(BORSCHT_ID, "Борщ", "main", ("lunch",)),
        _classified_dish(BUCKWHEAT_ID, "Гречка с мясом", "main", ("dinner",)),
        _classified_dish(
            BREAD_ID,
            "Хлеб",
            "addition",
            ("breakfast", "lunch", "dinner"),
            is_repeatable=True,
        ),
        _classified_dish(
            TEA_ID,
            "Чай",
            "drink",
            ("breakfast", "lunch", "dinner"),
            is_repeatable=True,
        ),
    ]
    db_session.add(project)
    for recipe, dish in classified:
        db_session.add_all([recipe, dish])
    db_session.commit()

    response = client.post("/api/v1/meal-plans/project/3/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["warnings"] == []
    assert {
        meal["meal_type"]: [dish["id"] for dish in meal["dishes"]]
        for meal in data["meals"]
    } == {
        "breakfast": [OATMEAL_ID, BREAD_ID, TEA_ID],
        "snack": [APPLE_ID],
        "lunch": [BORSCHT_ID, BREAD_ID, TEA_ID],
        "dinner": [BUCKWHEAT_ID, BREAD_ID, TEA_ID],
    }
    assert [item["dish_id"] for item in data["items"]] == [
        OATMEAL_ID,
        BREAD_ID,
        TEA_ID,
        APPLE_ID,
        BORSCHT_ID,
        BREAD_ID,
        TEA_ID,
        BUCKWHEAT_ID,
        BREAD_ID,
        TEA_ID,
    ]
