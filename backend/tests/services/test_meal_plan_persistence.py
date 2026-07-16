from types import SimpleNamespace

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
):
    return SimpleNamespace(
        id=dish_id,
        name=name,
        recipe=SimpleNamespace(is_archived=False),
        meal_roles=list(assignments),
    )


class FakeDishRepository:
    def __init__(self, dishes=None):
        self.dishes = dishes or [
            _dish("dish-1", "Овсяная каша", _assignment("main", "breakfast")),
            _dish("dish-2", "Борщ", _assignment("main", "dinner")),
        ]

    def list(self):
        return self.dishes


class FakeMealPlanRepository:
    def __init__(self):
        self.meal_plans = []
        self.days = []
        self.items = []
        self.slots = []
        self.slot_dishes = []
        self.committed = False
        self.meal_plan = None

    def add(self, meal_plan):
        self.meal_plans.append(meal_plan)
        self.meal_plan = meal_plan

    def add_day(self, day):
        self.days.append(day)

    def add_item(self, item):
        self.items.append(item)

    def add_slot(self, slot):
        self.slots.append(slot)

    def add_slot_dish(self, slot_dish):
        self.slot_dishes.append(slot_dish)

    def commit(self):
        self.committed = True

    def get_with_details(self, meal_plan_id: str):
        return self.meal_plan


def test_generate_and_save_meal_plan():
    repository = FakeMealPlanRepository()
    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        meal_plan_repository=repository,
    )

    result = service.generate_and_save(
        name="Altai Trip",
        participants=10,
        days=2,
        meals_per_day=["breakfast", "dinner"],
    )

    assert result.name == "Altai Trip"
    assert result.participants == 10
    assert result.days_count == 2
    assert len(repository.meal_plans) == 1
    assert len(repository.days) == 2
    assert len(repository.items) == 4
    assert len(repository.slots) == 4
    assert [slot.order for slot in repository.slots] == [0, 1, 0, 1]
    assert len(repository.slot_dishes) == 4
    assert repository.committed is True


def test_generate_and_save_result_preserves_generator_warnings():
    repository = FakeMealPlanRepository()
    service = MealPlanService(
        dish_repository=FakeDishRepository(
            dishes=[
                _dish(
                    "dish-1",
                    "Овсяная каша",
                    _assignment("main", "breakfast"),
                ),
            ]
        ),
        meal_plan_repository=repository,
    )

    saved = service.generate_and_save_result(
        name="Short catalogue",
        participants=4,
        days=1,
        meals_per_day=["breakfast", "dinner"],
    )

    assert saved.meal_plan.name == "Short catalogue"
    assert saved.warnings == ["No main dishes available for dinner"]


def test_generate_and_save_preserves_composition_order():
    repository = FakeMealPlanRepository()
    service = MealPlanService(
        dish_repository=FakeDishRepository(
            dishes=[
                _dish(
                    "main",
                    "Овсяная каша",
                    _assignment("main", "breakfast"),
                ),
                _dish(
                    "addition",
                    "Бутерброд",
                    _assignment("addition", "breakfast"),
                ),
                _dish(
                    "drink",
                    "Чай",
                    _assignment("drink", "breakfast"),
                ),
            ]
        ),
        meal_plan_repository=repository,
    )

    saved = service.generate_and_save_result(
        name="Breakfast composition",
        participants=4,
        days=1,
        meals_per_day=["breakfast"],
    )

    assert saved.warnings == []
    assert [item.dish_id for item in repository.items] == [
        "main",
        "addition",
        "drink",
    ]
    assert [slot_dish.dish_id for slot_dish in repository.slot_dishes] == [
        "main",
        "addition",
        "drink",
    ]
    assert [slot_dish.order for slot_dish in repository.slot_dishes] == [0, 1, 2]
