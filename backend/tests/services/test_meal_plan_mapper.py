from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.services.meal_plan_mapper import MealPlanMapper


DISH_ID = "550e8400-e29b-41d4-a716-446655440001"
RECIPE_ID = "660e8400-e29b-41d4-a716-446655440001"
PLAN_ID = "ea557e05-d89b-4403-9822-5bc3a95c8f2c"


def test_mapper_prefers_meal_slots_and_exposes_membership_id():
    recipe = RecipeORM(id=RECIPE_ID, name="Recipe")
    dish = DishORM(id=DISH_ID, name="Pilaf", recipe=recipe)
    meal_plan = MealPlanORM(
        id=PLAN_ID,
        name="Trip",
        participants=4,
        days_count=1,
    )
    day = MealPlanDayORM(id="day", meal_plan=meal_plan, day_number=1)
    MealPlanItemORM(
        id="legacy-item",
        day=day,
        dish=dish,
        dish_id=dish.id,
        meal_type="dinner",
    )
    slot = MealSlotORM(id="slot", day=day, meal_type="dinner", order=0)
    MealSlotDishORM(
        id="slot-dish",
        slot=slot,
        dish=dish,
        dish_id=dish.id,
        order=0,
    )

    response = MealPlanMapper.to_response(meal_plan)

    assert len(response.items) == 1
    assert len(response.meals) == 1
    assert response.meals[0].dishes[0].id == "slot-dish"
