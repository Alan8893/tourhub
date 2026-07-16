import pytest

from app.engines.meal_composition_policy import (
    MealCompositionPolicy,
    SelectionContext,
)
from app.engines.meal_plan_generator import DishInput, DishRoleInput
from app.modules.domain.meal_role import MealRole


def classified_dish(*, is_repeatable: bool = False) -> DishInput:
    return DishInput(
        id="1",
        name="Pilaf",
        meal_roles=(
            DishRoleInput(
                role="main",
                allowed_meal_types=frozenset(("lunch",)),
                is_repeatable=is_repeatable,
            ),
        ),
    )


def test_policy_rejects_same_day_non_repeatable_duplicate():
    dish = classified_dish()
    context = SelectionContext(used_for_day={"1"})

    assert (
        MealCompositionPolicy.can_select(
            dish,
            context,
            meal_type="lunch",
            role=MealRole.MAIN,
        )
        is False
    )


def test_policy_allows_unused_compatible_dish():
    dish = classified_dish()
    context = SelectionContext(used_for_day=set())

    assert (
        MealCompositionPolicy.can_select(
            dish,
            context,
            meal_type="lunch",
            role=MealRole.MAIN,
        )
        is True
    )


def test_policy_allows_repeatable_same_day_dish():
    dish = classified_dish(is_repeatable=True)
    context = SelectionContext(used_for_day={"1"})

    assert (
        MealCompositionPolicy.can_select(
            dish,
            context,
            meal_type="lunch",
            role=MealRole.MAIN,
        )
        is True
    )


def test_policy_rejects_meal_type_not_allowed_by_assignment():
    dish = classified_dish()
    context = SelectionContext(used_for_day=set())

    assert (
        MealCompositionPolicy.can_select(
            dish,
            context,
            meal_type="breakfast",
            role=MealRole.MAIN,
        )
        is False
    )


def test_policy_maps_required_roles():
    assert MealCompositionPolicy.required_role("breakfast") is MealRole.MAIN
    assert MealCompositionPolicy.required_role("lunch") is MealRole.MAIN
    assert MealCompositionPolicy.required_role("dinner") is MealRole.MAIN
    assert MealCompositionPolicy.required_role("snack") is MealRole.SNACK


def test_policy_rejects_unknown_meal_type():
    with pytest.raises(ValueError, match="Unsupported meal type"):
        MealCompositionPolicy.required_role("brunch")


def test_context_registers_selection_and_resets_for_next_day():
    dish = classified_dish()
    context = SelectionContext(used_for_day=set())

    context.register_selected(dish)
    assert context.used_for_day == {"1"}

    context.reset_day()
    assert context.used_for_day == set()
