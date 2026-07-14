from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class FakeShoppingListService:
    def __init__(self):
        self.calls = []

    def calculate_for_recipes(self, recipes, people, days):
        self.calls.append((recipes, people, days))
        return recipes

    def calculate_packaged_for_recipes(self, recipes, people, days):
        self.calls.append((recipes, people, days))
        return recipes


class FakeRecipe:
    def __init__(self, recipe_id):
        self.id = recipe_id


class FakeDish:
    def __init__(self, recipe_id):
        self.recipe = FakeRecipe(recipe_id)


def make_slot(recipe_ids):
    slot = MealSlotORM(id="slot-1", meal_type="breakfast")
    slot.dishes = []
    for index, recipe_id in enumerate(recipe_ids):
        slot_dish = MealSlotDishORM(
            id=f"slot-dish-{index}",
            dish_id=f"dish-{index}",
        )
        slot_dish.dish = FakeDish(recipe_id)
        slot.dishes.append(slot_dish)
    return slot


def test_shopping_collects_recipe_occurrences_from_meal_slots():
    day = MealPlanDayORM(id="day-1", day_number=1)
    day.slots = [make_slot(["recipe-1"])]
    day.items = []

    meal_plan = MealPlanORM(id="plan-1", participants=5, days_count=1)
    meal_plan.days = [day]

    service = MealPlanShoppingService(FakeShoppingListService())

    result = service._collect_recipe_occurrences(meal_plan)

    assert [recipe.id for recipe in result] == ["recipe-1"]


def test_shopping_preserves_repeated_recipe_occurrences():
    first_day = MealPlanDayORM(id="day-1", day_number=1)
    first_day.slots = [make_slot(["recipe-1"])]
    first_day.items = []

    second_day = MealPlanDayORM(id="day-2", day_number=2)
    second_day.slots = [make_slot(["recipe-1"])]
    second_day.items = []

    meal_plan = MealPlanORM(id="plan-1", participants=5, days_count=2)
    meal_plan.days = [first_day, second_day]

    service = MealPlanShoppingService(FakeShoppingListService())

    result = service._collect_recipe_occurrences(meal_plan)

    assert [recipe.id for recipe in result] == ["recipe-1", "recipe-1"]


def test_slots_take_priority_over_legacy_items_for_same_day():
    day = MealPlanDayORM(id="day-1", day_number=1)
    day.slots = [make_slot(["slot-recipe"])]

    legacy_item = MealPlanItemORM(
        id="legacy-item",
        dish_id="legacy-dish",
        meal_type="breakfast",
    )
    legacy_item.dish = FakeDish("legacy-recipe")
    day.items = [legacy_item]

    meal_plan = MealPlanORM(id="plan-1", participants=5, days_count=1)
    meal_plan.days = [day]

    service = MealPlanShoppingService(FakeShoppingListService())

    result = service._collect_recipe_occurrences(meal_plan)

    assert [recipe.id for recipe in result] == ["slot-recipe"]


def test_calculation_uses_current_participant_count_and_single_occurrence_day():
    day = MealPlanDayORM(id="day-1", day_number=1)
    day.slots = [make_slot(["recipe-1"])]
    day.items = []

    meal_plan = MealPlanORM(id="plan-1", participants=20, days_count=5)
    meal_plan.days = [day]

    shopping_service = FakeShoppingListService()
    service = MealPlanShoppingService(shopping_service)

    service.calculate(meal_plan)

    recipes, people, days = shopping_service.calls[0]
    assert [recipe.id for recipe in recipes] == ["recipe-1"]
    assert people == 20
    assert days == 1
