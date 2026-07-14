from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM


def seed_slot(db_session):
    recipe = RecipeORM(id="recipe-1", name="Club porridge")
    dish = DishORM(id="dish-1", name="Porridge", recipe_id=recipe.id)
    plan = MealPlanORM(
        id="plan-1",
        name="Test trip",
        participants=10,
        days_count=1,
    )
    day = MealPlanDayORM(
        id="day-1",
        meal_plan=plan,
        day_number=1,
    )
    slot = MealSlotORM(
        id="slot-1",
        day=day,
        meal_type="breakfast",
        order=0,
    )
    slot_dish = MealSlotDishORM(
        id="slot-dish-1",
        slot=slot,
        dish=dish,
        order=0,
    )
    db_session.add_all([recipe, dish, plan, day, slot, slot_dish])
    db_session.commit()


def test_remove_unknown_slot_dish_returns_404(client, db_session):
    seed_slot(db_session)

    response = client.delete(
        "/api/v1/meal-slots/slot-1/dishes/missing-slot-dish"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Meal slot dish not found"
    assert data["request_id"]


def test_replace_unknown_slot_dish_returns_404(client, db_session):
    seed_slot(db_session)

    response = client.put(
        "/api/v1/meal-slots/slot-1/dishes/missing-slot-dish/dish-1"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "Meal slot dish not found"
    assert data["request_id"]


def test_legacy_meal_plan_placeholder_is_not_public(client):
    response = client.post(
        "/api/v1/meal-plans/",
        json={
            "name": "Test trip",
            "participants": 10,
            "days": 1,
            "meals_per_day": ["breakfast"],
        },
    )

    assert response.status_code == 404
