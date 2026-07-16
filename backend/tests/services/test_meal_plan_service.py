from types import SimpleNamespace

from app.engines.meal_plan_generator import MealPlanGenerator
from app.services.meal_plan_service import MealPlanService


def classified_dish(
    dish_id: str,
    name: str,
    *,
    meal_types: tuple[str, ...],
    is_archived: bool = False,
):
    return SimpleNamespace(
        id=dish_id,
        name=name,
        recipe=SimpleNamespace(is_archived=is_archived),
        meal_roles=[
            SimpleNamespace(
                role="main",
                is_repeatable=False,
                meal_types=[SimpleNamespace(meal_type=value) for value in meal_types],
            )
        ],
    )


class FakeDishRepository:
    """Fake repository for service unit tests."""

    def list(self):
        return [
            classified_dish(
                "1",
                "Pilaf",
                meal_types=("breakfast", "lunch", "dinner"),
            ),
            classified_dish(
                "2",
                "Soup",
                meal_types=("lunch", "dinner"),
            ),
        ]


def test_meal_plan_service_generates_plan_from_persisted_classification():
    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        generator=MealPlanGenerator(),
    )

    result = service.generate(
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert len(result.items) == 4
    assert result.items[0].day_number == 1
    assert result.items[0].meal_type == "breakfast"
    assert result.items[0].dish_name == "Pilaf"
    assert all(
        item.dish_name != "Soup"
        for item in result.items
        if item.meal_type == "breakfast"
    )


def test_meal_plan_service_excludes_archived_recipe_dishes():
    class Repository:
        def list(self):
            return [
                classified_dish(
                    "archived",
                    "Archived porridge",
                    meal_types=("breakfast",),
                    is_archived=True,
                ),
                classified_dish(
                    "active",
                    "Active porridge",
                    meal_types=("breakfast",),
                ),
            ]

    result = MealPlanService(dish_repository=Repository()).generate(
        days=1,
        meals_per_day=["breakfast"],
    )

    assert [item.dish_id for item in result.items] == ["active"]


def test_meal_plan_service_keeps_unclassified_dishes_out_of_generation():
    class Repository:
        def list(self):
            return [
                SimpleNamespace(
                    id="unclassified",
                    name="Manual only",
                    recipe=SimpleNamespace(is_archived=False),
                    meal_roles=[],
                )
            ]

    result = MealPlanService(dish_repository=Repository()).generate(
        days=1,
        meals_per_day=["breakfast"],
    )

    assert result.items == []
    assert result.slots[0].dishes == []
    assert result.warnings == ["No compatible main dishes available for breakfast"]
