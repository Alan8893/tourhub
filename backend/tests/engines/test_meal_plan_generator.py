from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerator,
)


def test_generate_meal_plan_without_repetition_warning():
    generator = MealPlanGenerator()

    dishes = [
        DishInput(id="1", name="Pilaf"),
        DishInput(id="2", name="Soup"),
        DishInput(id="3", name="Oatmeal"),
        DishInput(id="4", name="Pasta"),
    ]

    result = generator.generate(
        dishes=dishes,
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert len(result.items) == 4
    assert result.warnings == []


def test_generate_meal_plan_uses_each_dish_once_per_day():
    generator = MealPlanGenerator()
    dishes = [
        DishInput(id="1", name="Pilaf"),
        DishInput(id="2", name="Soup"),
        DishInput(id="3", name="Oatmeal"),
        DishInput(id="4", name="Pasta"),
    ]

    result = generator.generate(
        dishes=dishes,
        days=2,
        meals_per_day=["breakfast", "snack", "lunch", "dinner"],
    )

    assert [item.dish_id for item in result.items if item.day_number == 1] == [
        "1",
        "2",
        "3",
        "4",
    ]


def test_main_dish_is_not_repeated_within_three_days():
    generator = MealPlanGenerator()
    dishes = [
        DishInput(id="1", name="Pilaf"),
        DishInput(id="2", name="Soup"),
        DishInput(id="3", name="Pasta"),
        DishInput(id="4", name="Curry"),
    ]

    result = generator.generate(
        dishes=dishes,
        days=4,
        meals_per_day=["dinner"],
    )

    assert [item.dish_id for item in result.items] == ["1", "2", "3", "4"]


def test_generate_meal_plan_returns_warning_when_not_enough_dishes():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[DishInput(id="1", name="Pilaf")],
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert "Dish database is insufficient" in result.warnings


def test_generate_meal_plan_repeats_deterministically_after_catalogue_exhaustion():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[DishInput(id="1", name="Pilaf"), DishInput(id="2", name="Soup")],
        days=1,
        meals_per_day=["breakfast", "snack", "lunch"],
    )

    assert [item.dish_id for item in result.items] == ["1", "2", "1"]
    assert result.warnings == ["Dish database is insufficient"]


def test_generate_empty_dishes_returns_warning():
    generator = MealPlanGenerator()

    result = generator.generate(dishes=[], days=3, meals_per_day=["breakfast"])

    assert result.items == []
    assert "No dishes available" in result.warnings
