from uuid import uuid4

from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.modules.projects.models.project import ProjectORM


def _seed_project(db_session):
    project = ProjectORM(id=61, name="Trip", participants=8, days=1, status="draft")
    plan = MealPlanORM(
        id=str(uuid4()),
        project=project,
        name="Plan",
        participants=8,
        days_count=1,
    )
    day = MealPlanDayORM(id=str(uuid4()), meal_plan=plan, day_number=1)
    first = MealSlotORM(id=str(uuid4()), day=day, meal_type="breakfast", order=0)
    second = MealSlotORM(id=str(uuid4()), day=day, meal_type="dinner", order=1)

    recipes = [RecipeORM(id=str(uuid4()), name=f"Recipe {index}") for index in range(3)]
    dishes = [
        DishORM(id=str(uuid4()), name=f"Dish {index}", recipe=recipe)
        for index, recipe in enumerate(recipes)
    ]
    first.dishes.extend(
        [
            MealSlotDishORM(id=str(uuid4()), dish=dishes[0], order=0),
            MealSlotDishORM(id=str(uuid4()), dish=dishes[1], order=1),
        ]
    )
    second.dishes.append(
        MealSlotDishORM(id=str(uuid4()), dish=dishes[2], order=0)
    )

    primary = RecipeEquipmentRequirementORM(
        id=str(uuid4()),
        recipe_id=recipes[0].id,
        equipment_name="Pot",
        quantity=1,
    )
    requirements = [
        primary,
        RecipeEquipmentRequirementORM(
            id=str(uuid4()),
            recipe_id=recipes[0].id,
            equipment_name="Stove",
            quantity=1,
        ),
        RecipeEquipmentRequirementORM(
            id=str(uuid4()),
            recipe_id=recipes[1].id,
            equipment_name="pot",
            quantity=2,
        ),
        RecipeEquipmentRequirementORM(
            id=str(uuid4()),
            recipe_id=recipes[2].id,
            equipment_name="Pot",
            quantity=2,
        ),
        RecipeEquipmentRequirementORM(
            id=str(uuid4()),
            recipe_id=recipes[2].id,
            equipment_name="Bowls",
            quantity=4,
        ),
    ]
    db_session.add_all([project, plan, day, first, second, *requirements])
    db_session.commit()
    return primary


def test_equipment_generation_uses_peak_meal_quantity(client, db_session):
    primary = _seed_project(db_session)

    response = client.post("/api/v1/equipment-lists/project/61/generate")
    assert response.status_code == 200
    payload = response.json()
    assert {
        (item["equipment_name"], item["required_quantity"])
        for item in payload["items"]
    } == {("Pot", 3), ("Stove", 1), ("Bowls", 4)}
    assert all(item["calculated_quantity"] == item["required_quantity"] for item in payload["items"])
    assert all(not item["is_manual"] for item in payload["items"])
    assert all(not item["is_overridden"] for item in payload["items"])

    primary.quantity = 4
    db_session.commit()
    refreshed = client.post("/api/v1/equipment-lists/project/61/generate").json()
    assert refreshed["id"] == payload["id"]
    pot = next(item for item in refreshed["items"] if item["equipment_name"] == "Pot")
    assert pot["required_quantity"] == 6
    assert pot["calculated_quantity"] == 6
    assert client.get("/api/v1/equipment-lists/project/61").json() == refreshed


def test_manual_equipment_changes_survive_regeneration(client, db_session):
    primary = _seed_project(db_session)
    generated = client.post("/api/v1/equipment-lists/project/61/generate").json()
    pot = next(item for item in generated["items"] if item["equipment_name"] == "Pot")
    stove = next(item for item in generated["items"] if item["equipment_name"] == "Stove")

    updated = client.put(
        f"/api/v1/equipment-lists/project/61/items/{pot['id']}",
        json={"required_quantity": 9},
    )
    assert updated.status_code == 200
    assert updated.json()["is_overridden"] is True

    removed = client.delete(
        f"/api/v1/equipment-lists/project/61/items/{stove['id']}"
    )
    assert removed.status_code == 204

    added = client.post(
        "/api/v1/equipment-lists/project/61/items",
        json={"equipment_name": "  Lantern  ", "required_quantity": 2},
    )
    assert added.status_code == 201
    lantern = added.json()
    assert lantern["equipment_name"] == "Lantern"
    assert lantern["calculated_quantity"] is None
    assert lantern["is_manual"] is True

    duplicate = client.post(
        "/api/v1/equipment-lists/project/61/items",
        json={"equipment_name": "lantern", "required_quantity": 1},
    )
    assert duplicate.status_code == 409

    primary.quantity = 4
    db_session.commit()
    refreshed = client.post("/api/v1/equipment-lists/project/61/generate").json()
    by_name = {item["equipment_name"]: item for item in refreshed["items"]}
    assert by_name["Pot"]["calculated_quantity"] == 6
    assert by_name["Pot"]["required_quantity"] == 9
    assert by_name["Pot"]["is_overridden"] is True
    assert "Stove" not in by_name
    assert by_name["Lantern"]["required_quantity"] == 2
    assert by_name["Lantern"]["is_manual"] is True

    restored = client.post(
        "/api/v1/equipment-lists/project/61/items",
        json={"equipment_name": "stove", "required_quantity": 5},
    )
    assert restored.status_code == 201
    assert restored.json()["calculated_quantity"] == 1
    assert restored.json()["is_overridden"] is True

    deleted_manual = client.delete(
        f"/api/v1/equipment-lists/project/61/items/{lantern['id']}"
    )
    assert deleted_manual.status_code == 204
    final_payload = client.post("/api/v1/equipment-lists/project/61/generate").json()
    final_by_name = {item["equipment_name"].casefold(): item for item in final_payload["items"]}
    assert "lantern" not in final_by_name
    assert final_by_name["stove"]["required_quantity"] == 5
