from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.meal_plan import MealPlanORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


MEAL_PLAN_ID = "ea557e05-d89b-4403-9822-5bc3a95c8f2c"
DISH_ID = "550e8400-e29b-41d4-a716-446655440001"
RECIPE_ID = "660e8400-e29b-41d4-a716-446655440001"
OATMEAL_DISH_ID = "550e8400-e29b-41d4-a716-446655440002"
SNACK_DISH_ID = "550e8400-e29b-41d4-a716-446655440003"
BORSCHT_DISH_ID = "550e8400-e29b-41d4-a716-446655440004"


def assign_role(
    dish: DishORM,
    role: str,
    meal_types: tuple[str, ...],
    *,
    is_repeatable: bool = False,
) -> None:
    dish.meal_roles.append(
        DishMealRoleORM(
            dish_id=dish.id,
            role=role,
            is_repeatable=is_repeatable,
            meal_types=[
                DishMealRoleMealTypeORM(
                    dish_id=dish.id,
                    role=role,
                    meal_type=meal_type,
                )
                for meal_type in meal_types
            ],
        )
    )


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
    assign_role(dish, "main", ("breakfast", "lunch", "dinner"))
    assign_role(dish, "snack", ("snack",))
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


def test_generate_project_meal_plan_respects_role_and_meal_type_compatibility(
    client,
    db_session,
):
    project = ProjectORM(
        id=3,
        name="Classified Catalogue",
        participants=4,
        days=1,
        first_meal="breakfast",
        last_meal="lunch",
        status="draft",
    )
    oatmeal_recipe = RecipeORM(id="recipe-oatmeal", name="Oatmeal recipe")
    snack_recipe = RecipeORM(id="recipe-snack", name="Snack recipe")
    borscht_recipe = RecipeORM(id="recipe-borscht", name="Borscht recipe")
    oatmeal = DishORM(id=OATMEAL_DISH_ID, name="Oatmeal", recipe=oatmeal_recipe)
    snack = DishORM(id=SNACK_DISH_ID, name="Trail snack", recipe=snack_recipe)
    borscht = DishORM(id=BORSCHT_DISH_ID, name="Borscht", recipe=borscht_recipe)
    assign_role(oatmeal, "main", ("breakfast",))
    assign_role(snack, "snack", ("snack",))
    assign_role(borscht, "main", ("lunch", "dinner"))
    db_session.add_all(
        [
            project,
            oatmeal_recipe,
            snack_recipe,
            borscht_recipe,
            oatmeal,
            snack,
            borscht,
        ]
    )
    db_session.commit()

    response = client.post("/api/v1/meal-plans/project/3/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["warnings"] == []
    assert [
        (meal["meal_type"], [dish["id"] for dish in meal["dishes"]])
        for meal in data["meals"]
    ] == [
        ("breakfast", [OATMEAL_DISH_ID]),
        ("snack", [SNACK_DISH_ID]),
        ("lunch", [BORSCHT_DISH_ID]),
    ]
