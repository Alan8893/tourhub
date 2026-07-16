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
                allowed_meal_types=frozenset(("breakfast",)),
            ),
        ),
    )


def test_generate_multiple_dishes_for_one_meal():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            classified_dish("1", "Porridge"),
            classified_dish("2", "Sandwiches"),
            classified_dish("3", "Tea"),
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
        dishes=[classified_dish("1", "Porridge")],
        days=1,
        meals_per_day=["breakfast"],
        dishes_per_meal=3,
    )

    assert len(result.items) == 3
    assert "Dish database is insufficient" in result.warnings
