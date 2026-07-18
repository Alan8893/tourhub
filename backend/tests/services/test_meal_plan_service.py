from types import SimpleNamespace

from app.engines.meal_plan_generator import MealPlanGenerator
from app.services.meal_plan_service import MealPlanService


def _assignment(role: str, *meal_types: str, is_repeatable: bool = False):
    return SimpleNamespace(
        role=role,
        is_repeatable=is_repeatable,
        meal_types=[SimpleNamespace(meal_type=meal_type) for meal_type in meal_types],
    )


def _dish(
    dish_id: str,
    name: str,
    *assignments,
    is_archived: bool = False,
):
    recipe_id = f"recipe-{dish_id}"
    return SimpleNamespace(
        id=dish_id,
        name=name,
        recipe_id=recipe_id,
        recipe=SimpleNamespace(
            id=recipe_id,
            name=f"{name} recipe",
            is_archived=is_archived,
        ),
        recipe_variants=[],
        meal_roles=list(assignments),
    )


class FakeDishRepository:
    def list(self):
        return [
            _dish(
                "1",
                "Овсяная каша",
                _assignment("main", "breakfast", is_repeatable=True),
            ),
            _dish(
                "2",
                "Борщ",
                _assignment("main", "dinner", is_repeatable=True),
            ),
        ]


def test_meal_plan_service_generates_plan():
    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        generator=MealPlanGenerator(),
    )

    result = service.generate(
        days=2,
        meals_per_day=[
            "breakfast",
            "dinner",
        ],
    )

    assert len(result.items) == 4
    assert result.items[0].day_number == 1
    assert result.items[0].meal_type == "breakfast"
    assert result.items[0].dish_name == "Овсяная каша"
    assert result.items[0].recipe_id == "recipe-1"
    assert result.items[1].meal_type == "dinner"
    assert result.items[1].dish_name == "Борщ"
    assert result.items[1].recipe_id == "recipe-2"
    assert result.warnings == []


def test_meal_plan_service_excludes_archived_recipes():
    class ArchivedDishRepository:
        def list(self):
            return [
                _dish(
                    "archived-oatmeal",
                    "Архивная каша",
                    _assignment("main", "breakfast"),
                    is_archived=True,
                ),
            ]

    service = MealPlanService(dish_repository=ArchivedDishRepository())

    result = service.generate(days=1, meals_per_day=["breakfast"])

    assert result.items == []
    assert len(result.slots) == 1
    assert result.slots[0].dishes == []
    assert result.warnings == ["No main dishes available for breakfast"]


def test_meal_plan_service_applies_calendar_day_main_diversity():
    class DiverseDishRepository:
        def list(self):
            return [
                _dish("main-a", "Main A", _assignment("main", "lunch")),
                _dish("main-b", "Main B", _assignment("main", "lunch")),
                _dish("main-c", "Main C", _assignment("main", "lunch")),
                _dish(
                    "archived-main",
                    "Archived main",
                    _assignment("main", "lunch"),
                    is_archived=True,
                ),
                _dish("unclassified", "Unclassified"),
            ]

    service = MealPlanService(dish_repository=DiverseDishRepository())

    result = service.generate(days=4, meals_per_day=["lunch"])

    assert [item.dish_id for item in result.items] == [
        "main-a",
        "main-b",
        "main-c",
        "main-a",
    ]
    assert [item.recipe_id for item in result.items] == [
        "recipe-main-a",
        "recipe-main-b",
        "recipe-main-c",
        "recipe-main-a",
    ]
    assert result.warnings == []
