from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerator,
)


def classified_dish(
    dish_id: str,
    name: str,
    *,
    role: str = "main",
    meal_types: tuple[str, ...] = ("breakfast", "lunch", "dinner"),
    is_repeatable: bool = False,
) -> DishInput:
    return DishInput(
        id=dish_id,
        name=name,
        meal_roles=(
            DishRoleInput(
                role=role,
                allowed_meal_types=frozenset(meal_types),
                is_repeatable=is_repeatable,
            ),
        ),
    )


def test_generate_meal_plan_without_repetition_warning():
    generator = MealPlanGenerator()
    dishes = [
        classified_dish("1", "Pilaf"),
        classified_dish("2", "Soup"),
        classified_dish("3", "Oatmeal"),
        classified_dish("4", "Pasta"),
    ]

    result = generator.generate(
        dishes=dishes,
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert len(result.items) == 4
    assert result.warnings == []


def test_generate_meal_plan_uses_compatible_dishes_once_per_day():
    generator = MealPlanGenerator()
    dishes = [
        classified_dish("1", "Porridge"),
        classified_dish("2", "Trail snack", role="snack", meal_types=("snack",)),
        classified_dish("3", "Soup"),
        classified_dish("4", "Pasta"),
    ]

    result = generator.generate(
        dishes=dishes,
        days=1,
        meals_per_day=["breakfast", "snack", "lunch", "dinner"],
    )

    assert [(item.meal_type, item.dish_id) for item in result.items] == [
        ("breakfast", "1"),
        ("snack", "2"),
        ("lunch", "3"),
        ("dinner", "4"),
    ]


def test_generate_meal_plan_returns_warning_when_not_enough_main_dishes():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[classified_dish("1", "Pilaf")],
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert "Dish database is insufficient" in result.warnings


def test_generate_meal_plan_repeats_deterministically_after_compatible_pool_exhaustion():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            classified_dish("1", "Pilaf"),
            classified_dish("2", "Soup"),
        ],
        days=1,
        meals_per_day=["breakfast", "lunch", "dinner"],
    )

    assert [item.dish_id for item in result.items] == ["1", "2", "1"]
    assert result.warnings == ["Dish database is insufficient"]


def test_generate_empty_dishes_returns_empty_slots_and_warnings():
    generator = MealPlanGenerator()

    result = generator.generate(dishes=[], days=1, meals_per_day=["breakfast"])

    assert result.items == []
    assert len(result.slots) == 1
    assert result.slots[0].dishes == []
    assert "No dishes available" in result.warnings
    assert "No compatible main dishes available for breakfast" in result.warnings


def test_lunch_only_soup_cannot_be_selected_for_breakfast():
    generator = MealPlanGenerator()
    soup = classified_dish("soup", "Borscht", meal_types=("lunch", "dinner"))
    porridge = classified_dish("porridge", "Oatmeal", meal_types=("breakfast",))

    result = generator.generate(
        dishes=[soup, porridge],
        days=1,
        meals_per_day=["breakfast", "lunch"],
    )

    assert [(item.meal_type, item.dish_id) for item in result.items] == [
        ("breakfast", "porridge"),
        ("lunch", "soup"),
    ]


def test_unclassified_dish_is_not_used_as_fallback():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[DishInput(id="unknown", name="Unclassified")],
        days=1,
        meals_per_day=["breakfast"],
    )

    assert result.items == []
    assert result.slots[0].dishes == []
    assert result.warnings == ["No compatible main dishes available for breakfast"]


def test_repeatable_assignment_can_be_reused_without_insufficient_warning():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[classified_dish("1", "Universal porridge", is_repeatable=True)],
        days=1,
        meals_per_day=["breakfast", "lunch", "dinner"],
    )

    assert [item.dish_id for item in result.items] == ["1", "1", "1"]
    assert result.warnings == []
