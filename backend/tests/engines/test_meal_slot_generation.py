from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerator,
)


def classified_dish(dish_id: str, name: str) -> DishInput:
    return DishInput(
        id=dish_id,
        name=name,
        meal_roles=(
            DishRoleInput(
                role="main",
                allowed_meal_types=frozenset(("breakfast", "lunch", "dinner")),
            ),
        ),
    )


def test_generator_creates_single_dish_slot():
    result = MealPlanGenerator().generate(
        dishes=[classified_dish("1", "Porridge")],
        days=1,
        meals_per_day=["breakfast"],
    )

    assert len(result.slots) == 1
    assert result.slots[0].meal_type == "breakfast"
    assert len(result.slots[0].dishes) == 1


def test_generator_creates_slot_with_multiple_dishes():
    result = MealPlanGenerator().generate(
        dishes=[
            classified_dish("1", "Porridge"),
            classified_dish("2", "Tea"),
        ],
        days=1,
        meals_per_day=["breakfast"],
        dishes_per_meal=2,
    )

    assert len(result.slots) == 1
    assert len(result.slots[0].dishes) == 2


def test_generator_keeps_legacy_items():
    result = MealPlanGenerator().generate(
        dishes=[classified_dish("1", "Soup")],
        days=1,
        meals_per_day=["lunch"],
    )

    assert len(result.items) == 1
    assert result.items[0].dish_name == "Soup"
