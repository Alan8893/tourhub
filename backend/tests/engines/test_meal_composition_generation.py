from app.engines.meal_plan_generator import DishInput, MealPlanGenerator


def test_generate_multiple_dishes_for_one_meal():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(id="1", name="Porridge"),
            DishInput(id="2", name="Sandwiches"),
            DishInput(id="3", name="Tea"),
        ],
        days=1,
        meals_per_day=["breakfast"],
        dishes_per_meal=3,
    )

    assert len(result.items) == 3
    assert all(item.meal_type == "breakfast" for item in result.items)


def test_meal_without_enough_dishes_returns_warning():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(id="1", name="Porridge"),
        ],
        days=1,
        meals_per_day=["breakfast"],
        dishes_per_meal=3,
    )

    assert len(result.items) == 3
    assert "Dish database is insufficient" in result.warnings
