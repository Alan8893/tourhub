from app.models.dish import DishORM
from app.services.meal_plan_service import MealPlanService


class FakeDishRepository:
    def __init__(self, dish_count: int = 2):
        self.dish_count = dish_count

    def list(self):
        dishes = [
            DishORM(id="dish-1", name="Pilaf", recipe_id="recipe-1"),
            DishORM(id="dish-2", name="Soup", recipe_id="recipe-2"),
        ]
        return dishes[: self.dish_count]


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
        dish_repository=FakeDishRepository(dish_count=1),
        meal_plan_repository=repository,
    )

    saved = service.generate_and_save_result(
        name="Short catalogue",
        participants=4,
        days=1,
        meals_per_day=["breakfast", "dinner"],
    )

    assert saved.meal_plan.name == "Short catalogue"
    assert saved.warnings == ["Dish database is insufficient"]
