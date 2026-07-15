from app.engines.meal_composition_policy import (
    MealCompositionPolicy,
    SelectionContext,
)
from app.engines.meal_plan_generator import DishInput


def test_policy_rejects_same_day_duplicate():
    dish = DishInput(id="1", name="Pilaf")
    context = SelectionContext(used_for_day={"1"})

    assert MealCompositionPolicy.can_select(dish, context) is False


def test_policy_allows_unused_dish():
    dish = DishInput(id="1", name="Pilaf")
    context = SelectionContext(used_for_day=set())

    assert MealCompositionPolicy.can_select(dish, context) is True


def test_context_registers_selection_and_resets_for_next_day():
    dish = DishInput(id="1", name="Pilaf")
    context = SelectionContext(used_for_day=set())

    context.register_selected(dish)
    assert context.used_for_day == {"1"}

    context.reset_day()
    assert context.used_for_day == set()
