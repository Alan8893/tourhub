from uuid import uuid4

from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.modules.projects.models.project import ProjectORM


def test_equipment_generation_uses_peak_meal_quantity(client, db_session):
    project = ProjectORM(id=61, name="Trip", participants=8, days=1, status="draft")
    plan = MealPlanORM(id=str(uuid4()), project=project, name="Plan", participants=8, days_count=1)
    day = MealPlanDayORM(id=str(uuid4()), meal_plan=plan, day_number=1)
    first = MealSlotORM(id=str(uuid4()), day=day, meal_type="breakfast", order=0)
    second = MealSlotORM(id=str(uuid4()), day=day, meal_type="dinner", order=1)

    recipes = [RecipeORM(id=str(uuid4()), name=f"Recipe {index}") for index in range(3)]
    dishes = [DishORM(id=str(uuid4()), name=f"Dish {index}", recipe=recipe) for index, recipe in enumerate(recipes)]
    first.dishes.extend([
        MealSlotDishORM(id=str(uuid4()), dish=dishes[0], order=0),
        MealSlotDishORM(id=str(uuid4()), dish=dishes[1], order=1),
    ])
    second.dishes.append(MealSlotDishORM(id=str(uuid4()), dish=dishes[2], order=0))

    primary = RecipeEquipmentRequirementORM(id=str(uuid4()), recipe_id=recipes[0].id, equipment_name="Pot", quantity=1)
    requirements = [
        primary,
        RecipeEquipmentRequirementORM(id=str(uuid4()), recipe_id=recipes[0].id, equipment_name="Stove", quantity=1),
        RecipeEquipmentRequirementORM(id=str(uuid4()), recipe_id=recipes[1].id, equipment_name="pot", quantity=2),
        RecipeEquipmentRequirementORM(id=str(uuid4()), recipe_id=recipes[2].id, equipment_name="Pot", quantity=2),
        RecipeEquipmentRequirementORM(id=str(uuid4()), recipe_id=recipes[2].id, equipment_name="Bowls", quantity=4),
    ]
    db_session.add_all([project, plan, day, first, second, *requirements])
    db_session.commit()

    response = client.post("/api/v1/equipment-lists/project/61/generate")
    assert response.status_code == 200
    payload = response.json()
    assert {(item["equipment_name"], item["required_quantity"]) for item in payload["items"]} == {("Pot", 3), ("Stove", 1), ("Bowls", 4)}

    primary.quantity = 4
    db_session.commit()
    refreshed = client.post("/api/v1/equipment-lists/project/61/generate").json()
    assert refreshed["id"] == payload["id"]
    assert next(item for item in refreshed["items"] if item["equipment_name"] == "Pot")["required_quantity"] == 6
    assert client.get("/api/v1/equipment-lists/project/61").json() == refreshed
