from app.engines.meal_plan_generator import (
    DishInput,
    DishRoleInput,
    MealPlanGenerator,
)
from app.engines.meal_schedule import MealScheduleDay


def _role(
    role: str,
    *meal_types: str,
    is_repeatable: bool = False,
) -> DishRoleInput:
    return DishRoleInput(
        role=role,
        allowed_meal_types=tuple(meal_types),
        is_repeatable=is_repeatable,
    )


def test_role_aware_generation_separates_breakfast_lunch_and_dinner():
    generator = MealPlanGenerator()
    result = generator.generate(
        dishes=[
            DishInput(
                id="oatmeal",
                name="Овсяная каша",
                meal_roles=(_role("main", "breakfast"),),
            ),
            DishInput(
                id="borscht",
                name="Борщ",
                meal_roles=(_role("main", "lunch"),),
            ),
            DishInput(
                id="buckwheat",
                name="Гречка с мясом",
                meal_roles=(_role("main", "dinner"),),
            ),
            DishInput(
                id="bread",
                name="Хлеб",
                meal_roles=(
                    _role(
                        "addition",
                        "breakfast",
                        "lunch",
                        "dinner",
                        is_repeatable=True,
                    ),
                ),
            ),
            DishInput(
                id="tea",
                name="Чай",
                meal_roles=(
                    _role(
                        "drink",
                        "breakfast",
                        "lunch",
                        "dinner",
                        is_repeatable=True,
                    ),
                ),
            ),
            DishInput(
                id="apple",
                name="Яблоко",
                meal_roles=(_role("snack", "snack"),),
            ),
        ],
        days=1,
        meals_per_day=["breakfast", "snack", "lunch", "dinner"],
        role_aware=True,
    )

    dishes_by_meal = {
        slot.meal_type: [dish.id for dish in slot.dishes]
        for slot in result.slots
    }

    assert dishes_by_meal == {
        "breakfast": ["oatmeal", "bread", "tea"],
        "snack": ["apple"],
        "lunch": ["borscht", "bread", "tea"],
        "dinner": ["buckwheat", "bread", "tea"],
    }
    assert "borscht" not in dishes_by_meal["breakfast"]
    assert "oatmeal" not in dishes_by_meal["lunch"]
    assert result.warnings == []


def test_role_aware_generation_excludes_unclassified_dishes():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[DishInput(id="mystery", name="Неклассифицированное блюдо")],
        days=1,
        meals_per_day=["breakfast"],
        role_aware=True,
    )

    assert result.items == []
    assert len(result.slots) == 1
    assert result.slots[0].dishes == []
    assert result.warnings == ["No main dishes available for breakfast"]


def test_role_aware_generation_does_not_warn_for_missing_optional_roles():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="oatmeal",
                name="Овсяная каша",
                meal_roles=(_role("main", "breakfast"),),
            ),
        ],
        days=1,
        meals_per_day=["breakfast"],
        role_aware=True,
    )

    assert [dish.id for dish in result.slots[0].dishes] == ["oatmeal"]
    assert result.warnings == []


def test_role_aware_generation_warns_when_required_role_is_exhausted():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="borscht",
                name="Борщ",
                meal_roles=(_role("main", "lunch"),),
            ),
        ],
        days=1,
        meals_per_day=["lunch", "lunch"],
        role_aware=True,
    )

    assert [dish.id for dish in result.slots[0].dishes] == ["borscht"]
    assert result.slots[1].dishes == []
    assert result.warnings == ["No eligible main dishes available for lunch"]


def test_role_aware_generation_allows_role_level_repetition():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="tea",
                name="Чай",
                meal_roles=(_role("drink", "breakfast", is_repeatable=True),),
            ),
            DishInput(
                id="oatmeal-1",
                name="Овсяная каша",
                meal_roles=(_role("main", "breakfast"),),
            ),
            DishInput(
                id="oatmeal-2",
                name="Пшённая каша",
                meal_roles=(_role("main", "breakfast"),),
            ),
        ],
        days=1,
        meals_per_day=["breakfast", "breakfast"],
        role_aware=True,
    )

    assert [[dish.id for dish in slot.dishes] for slot in result.slots] == [
        ["oatmeal-1", "tea"],
        ["oatmeal-2", "tea"],
    ]
    assert result.warnings == []


def test_main_diversity_uses_calendar_days_not_selection_count():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="breakfast-a",
                name="Каша A",
                meal_roles=(_role("main", "breakfast"),),
            ),
            DishInput(
                id="breakfast-b",
                name="Каша B",
                meal_roles=(_role("main", "breakfast"),),
            ),
            DishInput(
                id="lunch",
                name="Обед",
                meal_roles=(_role("main", "lunch"),),
            ),
            DishInput(
                id="dinner",
                name="Ужин",
                meal_roles=(_role("main", "dinner"),),
            ),
        ],
        days=2,
        schedule=[
            MealScheduleDay(
                day_number=1,
                meals=["breakfast", "lunch", "dinner", "breakfast"],
            ),
            MealScheduleDay(day_number=2, meals=["breakfast"]),
        ],
        role_aware=True,
    )

    assert [[dish.id for dish in slot.dishes] for slot in result.slots] == [
        ["breakfast-a"],
        ["lunch"],
        ["dinner"],
        ["breakfast-b"],
        [],
    ]
    assert result.warnings == ["No eligible main dishes available for breakfast"]


def test_main_diversity_rotates_candidates_and_reuses_on_day_four():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="main-a",
                name="Main A",
                meal_roles=(_role("main", "lunch"),),
            ),
            DishInput(
                id="main-b",
                name="Main B",
                meal_roles=(_role("main", "lunch"),),
            ),
            DishInput(
                id="main-c",
                name="Main C",
                meal_roles=(_role("main", "lunch"),),
            ),
        ],
        days=4,
        meals_per_day=["lunch"],
        role_aware=True,
    )

    assert [item.dish_id for item in result.items] == [
        "main-a",
        "main-b",
        "main-c",
        "main-a",
    ]
    assert result.warnings == []


def test_main_diversity_warns_deterministically_when_pool_is_exhausted():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="main-a",
                name="Main A",
                meal_roles=(_role("main", "lunch"),),
            ),
        ],
        days=4,
        meals_per_day=["lunch"],
        role_aware=True,
    )

    assert [[dish.id for dish in slot.dishes] for slot in result.slots] == [
        ["main-a"],
        [],
        [],
        ["main-a"],
    ]
    assert result.warnings == ["No eligible main dishes available for lunch"]


def test_repeatable_main_bypasses_calendar_day_diversity():
    generator = MealPlanGenerator()

    result = generator.generate(
        dishes=[
            DishInput(
                id="repeatable-main",
                name="Repeatable main",
                meal_roles=(
                    _role("main", "dinner", is_repeatable=True),
                ),
            ),
        ],
        days=3,
        meals_per_day=["dinner"],
        role_aware=True,
    )

    assert [item.dish_id for item in result.items] == [
        "repeatable-main",
        "repeatable-main",
        "repeatable-main",
    ]
    assert result.warnings == []
