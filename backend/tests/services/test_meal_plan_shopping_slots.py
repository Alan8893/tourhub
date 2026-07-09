from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class FakeShoppingListService:
    def calculate_for_recipes(self, recipes, people, days):
        return recipes

    def calculate_packaged_for_recipes(self, recipes, people, days):
        return recipes


class FakeRecipe:
    def __init__(self, recipe_id):
        self.id = recipe_id


class FakeDish:
    def __init__(self, recipe_id):
        self.recipe = FakeRecipe(recipe_id)



def test_shopping_collects_recipes_from_meal_slots():
    slot_dish = MealSlotDishORM(
        id="slot-dish-1",
        dish_id="dish-1",
    )
    slot_dish.dish = FakeDish("recipe-1")

    slot = MealSlotORM(
        id="slot-1",
        meal_type="breakfast",
    )
    slot.dishes = [slot_dish]

    day = MealPlanDayORM(
        id="day-1",
        day_number=1,
    )
    day.slots = [slot]
    day.items = []

    meal_plan = MealPlanORM(
        id="plan-1",
        participants=5,
        days_count=1,
    )
    meal_plan.days = [day]

    service = MealPlanShoppingService(FakeShoppingListService())

    result = service._collect_recipes(meal_plan)

    assert len(result) == 1
    assert result[0].id == "recipe-1"



def test_shopping_removes_duplicate_recipes():
    first = MealSlotDishORM(id="1", dish_id="dish-1")
    second = MealSlotDishORM(id="2", dish_id="dish-2")

    first.dish = FakeDish("recipe-1")
    second.dish = FakeDish("recipe-1")

    slot = MealSlotORM(id="slot-1", meal_type="dinner")
    slot.dishes = [first, second]

    day = MealPlanDayORM(id="day-1", day_number=1)
    day.slots = [slot]
    day.items = []

    meal_plan = MealPlanORM(id="plan-1", participants=5, days_count=1)
    meal_plan.days = [day]

    service = MealPlanShoppingService(FakeShoppingListService())

    result = service._collect_recipes(meal_plan)

    assert len(result) == 1
