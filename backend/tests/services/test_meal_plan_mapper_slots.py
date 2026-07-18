from uuid import uuid4

from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.services.meal_plan_mapper import MealPlanMapper


class FakeDish:
    def __init__(self, dish_id: str, name: str, recipe: RecipeORM):
        self.id = dish_id
        self.name = name
        self.recipe_id = recipe.id
        self.recipe = recipe


def test_mapper_returns_meal_slots_with_multiple_dishes():
    first_id = str(uuid4())
    second_id = str(uuid4())
    first_recipe = RecipeORM(id=str(uuid4()), name="Porridge recipe")
    second_recipe = RecipeORM(id=str(uuid4()), name="Tea recipe")

    first = MealSlotDishORM(
        id=str(uuid4()),
        dish_id=first_id,
        recipe_id=first_recipe.id,
        order=0,
    )
    first.dish = FakeDish(first_id, "Porridge", first_recipe)
    first.recipe = first_recipe

    second = MealSlotDishORM(
        id=str(uuid4()),
        dish_id=second_id,
        recipe_id=second_recipe.id,
        order=1,
    )
    second.dish = FakeDish(second_id, "Tea", second_recipe)
    second.recipe = second_recipe

    slot = MealSlotORM(
        id=str(uuid4()),
        meal_type="breakfast",
    )
    slot.dishes = [first, second]

    day = MealPlanDayORM(
        id=str(uuid4()),
        day_number=1,
    )
    day.slots = [slot]
    day.items = []

    meal_plan = MealPlanORM(
        id=str(uuid4()),
        name="Trip",
        participants=2,
        days_count=1,
    )
    meal_plan.days = [day]

    result = MealPlanMapper.to_response(meal_plan)

    assert len(result.meals) == 1
    assert result.meals[0].meal_type == "breakfast"
    assert len(result.meals[0].dishes) == 2
    assert result.meals[0].dishes[0].dish_name == "Porridge"
    assert result.meals[0].dishes[0].recipe_name == "Porridge recipe"
    assert result.meals[0].dishes[1].dish_name == "Tea"
    assert result.meals[0].dishes[1].recipe_name == "Tea recipe"
