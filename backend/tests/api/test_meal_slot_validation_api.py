from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


def test_meal_slot_rejects_dish_with_archived_recipe(client, db_session):
    project = ProjectORM(
        id=30,
        name="Trip",
        participants=4,
        days=1,
        status="draft",
    )
    meal_plan = MealPlanORM(
        id="550e8400-e29b-41d4-a716-446655440010",
        project=project,
        name="Trip",
        participants=4,
        days_count=1,
    )
    day = MealPlanDayORM(id="day", meal_plan=meal_plan, day_number=1)
    slot = MealSlotORM(id="slot", day=day, meal_type="dinner")
    recipe = RecipeORM(id="archived-recipe", name="Archived", is_archived=True)
    dish = DishORM(id="archived-dish", name="Archived dish", recipe=recipe)
    db_session.add_all([project, meal_plan, day, slot, recipe, dish])
    db_session.commit()

    response = client.post("/api/v1/meal-slots/slot/dishes/archived-dish")

    assert response.status_code == 422
    assert response.json()["error"] == (
        "Dish has no recipe available for the project generation mode"
    )
