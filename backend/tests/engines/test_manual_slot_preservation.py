import pytest

from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerator,
    PreservedMealSlotInput,
)


def _role(role: str, *meal_types: str) -> DishRoleInput:
    return DishRoleInput(role=role, allowed_meal_types=tuple(meal_types))


def test_preserved_manual_slot_bypasses_automatic_composition_and_warning():
    generator = MealPlanGenerator()
    manual_dish = DishInput(id="manual", name="Manual unclassified dish")

    result = generator.generate(
        dishes=[
            DishInput(
                id="lunch",
                name="Generated lunch",
                meal_roles=(_role("main", "lunch"),),
            ),
        ],
        days=1,
        meals_per_day=["breakfast", "lunch"],
        role_aware=True,
        preserved_slots=[
            PreservedMealSlotInput(
                day_number=1,
                meal_type="breakfast",
                dishes=[manual_dish],
            ),
        ],
    )

    assert [[dish.id for dish in slot.dishes] for slot in result.slots] == [
        ["manual"],
        ["lunch"],
    ]
    assert result.slots[0].is_manually_edited is True
    assert result.slots[1].is_manually_edited is False
    assert [item.dish_id for item in result.items] == ["manual", "lunch"]
    assert result.warnings == []


def test_preserved_empty_slot_remains_empty_without_required_role_warning():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[],
        days=1,
        meals_per_day=["breakfast"],
        role_aware=True,
        preserved_slots=[
            PreservedMealSlotInput(
                day_number=1,
                meal_type="breakfast",
                dishes=[],
            ),
        ],
    )

    assert result.items == []
    assert len(result.slots) == 1
    assert result.slots[0].dishes == []
    assert result.slots[0].is_manually_edited is True
    assert result.warnings == []


def test_preserved_slots_must_be_unique_by_day_and_meal_type():
    generator = MealPlanGenerator()
    preserved = PreservedMealSlotInput(
        day_number=1,
        meal_type="lunch",
        dishes=[],
    )

    with pytest.raises(
        ValueError,
        match="preserved meal slots must be unique by day and meal type",
    ):
        generator.generate(
            dishes=[],
            days=1,
            meals_per_day=["lunch"],
            role_aware=True,
            preserved_slots=[preserved, preserved],
        )
