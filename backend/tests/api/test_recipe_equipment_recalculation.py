from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.modules.projects.models.project import ProjectORM


def _add_project(db_session, project_id: int, recipe: RecipeORM, dish: DishORM) -> None:
    project = ProjectORM(
        id=project_id,
        name=f"Trip {project_id}",
        participants=8,
        days=1,
        status="prepared",
    )
    plan = MealPlanORM(
        id=f"plan-{project_id}",
        project=project,
        name=f"Plan {project_id}",
        participants=8,
        days_count=1,
    )
    day = MealPlanDayORM(
        id=f"day-{project_id}",
        meal_plan=plan,
        day_number=1,
    )
    slot = MealSlotORM(
        id=f"slot-{project_id}",
        day=day,
        meal_type="dinner",
        order=0,
    )
    slot.dishes.append(
        MealSlotDishORM(
            id=f"slot-dish-{project_id}",
            dish=dish,
            order=0,
        )
    )
    db_session.add_all([project, plan, day, slot])


def _items(client, project_id: int) -> dict[str, dict]:
    response = client.get(f"/api/v1/equipment-lists/project/{project_id}")
    assert response.status_code == 200
    return {item["equipment_name"]: item for item in response.json()["items"]}


def test_recipe_requirement_changes_refresh_prepared_equipment_lists(client, db_session):
    recipe = RecipeORM(id="shared-recipe", name="Shared recipe")
    dish = DishORM(id="shared-dish", name="Shared dish", recipe=recipe)
    pot = RecipeEquipmentRequirementORM(
        id="pot-requirement",
        recipe_id=recipe.id,
        equipment_name="Pot",
        quantity=2,
    )
    db_session.add_all([recipe, dish, pot])
    for project_id in (71, 72, 73):
        _add_project(db_session, project_id, recipe, dish)
    db_session.commit()

    first = client.post("/api/v1/equipment-lists/project/71/generate").json()
    second = client.post("/api/v1/equipment-lists/project/72/generate").json()
    first_pot = next(item for item in first["items"] if item["equipment_name"] == "Pot")
    assert client.put(
        f"/api/v1/equipment-lists/project/71/items/{first_pot['id']}",
        json={"required_quantity": 9},
    ).status_code == 200

    added = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "Stove", "quantity": 1},
    )
    assert added.status_code == 201
    assert _items(client, 71)["Stove"]["calculated_quantity"] == 1
    assert _items(client, 72)["Stove"]["calculated_quantity"] == 1
    assert client.get("/api/v1/equipment-lists/project/73").status_code == 404

    updated = client.put(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{pot.id}",
        json={"equipment_name": "Pot", "quantity": 4},
    )
    assert updated.status_code == 200
    first_items = _items(client, 71)
    second_items = _items(client, 72)
    assert first_items["Pot"]["calculated_quantity"] == 4
    assert first_items["Pot"]["required_quantity"] == 9
    assert first_items["Pot"]["is_overridden"] is True
    assert second_items["Pot"]["calculated_quantity"] == 4
    assert second_items["Pot"]["required_quantity"] == 4

    deleted = client.delete(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{pot.id}"
    )
    assert deleted.status_code == 204
    first_items = _items(client, 71)
    second_items = _items(client, 72)
    assert first_items["Pot"]["calculated_quantity"] is None
    assert first_items["Pot"]["required_quantity"] == 9
    assert first_items["Pot"]["is_manual"] is True
    assert "Pot" not in second_items
    assert "Stove" in first_items
    assert "Stove" in second_items
