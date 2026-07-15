from app.engines.meal_composition_policy import (
    MealCompositionPolicy,
    SelectionContext,
)
from app.engines.meal_plan_generator import DishInput


def test_policy_rejects_same_day_duplicate():
    dish = DishInput(id="1", name="Pilaf")
    context = SelectionContext(used_for_day={"1"}, recent_main_ids=set())

    assert MealCompositionPolicy.can_select(dish, context) is False


def test_policy_rejects_recent_main_dish():
    dish = DishInput(id="1", name="Pilaf", is_main=True)
    context = SelectionContext(used_for_day=set(), recent_main_ids={"1"})

    assert MealCompositionPolicy.can_select(dish, context) is False


def test_policy_allows_available_dish():
    dish = DishInput(id="1", name="Pilaf")
    context = SelectionContext(used_for_day=set(), recent_main_ids=set())

    assert MealCompositionPolicy.can_select(dish, context) is True
