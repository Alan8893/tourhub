from app.engines.meal_plan_generator import (
    DishInput,
    MealPlanGenerator,
)


def test_generate_meal_plan_without_repetition_warning():
    generator = MealPlanGenerator()

    dishes = [
        DishInput(
            id="1",
            name="Pilaf",
        ),
        DishInput(
            id="2",
            name="Soup",
        ),
        DishInput(
            id="3",
            name="Oatmeal",
        ),
        DishInput(
            id="4",
            name="Pasta",
        ),
    ]

    result = generator.generate(
        dishes=dishes,
        days=2,
        meals_per_day=[
            "breakfast",
            "dinner",
        ],
    )

    assert len(result.items) == 4
    assert result.warnings == []

    assert result.items[0].day_number == 1
    assert result.items[0].meal_type == "breakfast"

    assert result.items[1].meal_type == "dinner"


def test_generate_meal_plan_returns_warning_when_not_enough_dishes():
    generator = MealPlanGenerator()

    dishes = [
        DishInput(
            id="1",
            name="Pilaf",
        ),
    ]

    result = generator.generate(
        dishes=dishes,
        days=2,
        meals_per_day=[
            "breakfast",
            "dinner",
        ],
    )

    assert len(result.items) == 4

    assert (
        "Dish database is insufficient"
        in result.warnings
    )


def test_generate_empty_dishes_returns_warning():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[],
        days=3,
        meals_per_day=[
            "breakfast",
            "dinner",
        ],
    )

    assert result.items == []

    assert (
        "No dishes available"
        in result.warnings
    )