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
    return SimpleNamespace(
        id=dish_id,
        name=name,
        recipe=SimpleNamespace(is_archived=is_archived),
        meal_roles=list(assignments),
    )


class FakeDishRepository:
    def list(self):
        return [
            _dish("1", "Овсяная каша", _assignment("main", "breakfast")),
            _dish("2", "Борщ", _assignment("main", "dinner")),
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
    assert result.items[1].meal_type == "dinner"
    assert result.items[1].dish_name == "Борщ"
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
