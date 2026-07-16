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


def test_policy_blocks_main_within_three_calendar_day_window():
    dish = DishInput(id="main-1", name="Pilaf")
    context = SelectionContext(used_for_day=set())

    context.begin_day(1)
    context.register_selected(dish, role="main")

    context.begin_day(2)
    assert MealCompositionPolicy.can_select(dish, context, role="main") is False

    context.begin_day(3)
    assert MealCompositionPolicy.can_select(dish, context, role="main") is False

    context.begin_day(4)
    assert MealCompositionPolicy.can_select(dish, context, role="main") is True


def test_policy_applies_cross_day_diversity_only_to_main_role():
    dish = DishInput(id="addition-1", name="Bread")
    context = SelectionContext(used_for_day=set())

    context.begin_day(1)
    context.register_selected(dish, role="addition")
    context.begin_day(2)

    assert MealCompositionPolicy.can_select(dish, context, role="addition") is True


def test_policy_allows_repeatable_main_inside_diversity_window():
    dish = DishInput(id="main-1", name="Porridge")
    context = SelectionContext(used_for_day=set())

    context.begin_day(1)
    context.register_selected(dish, role="main")
    context.begin_day(2)

    assert MealCompositionPolicy.can_select(
        dish,
        context,
        is_repeatable=True,
        role="main",
    ) is True
