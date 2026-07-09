from app.models.dish import DishORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.dish_repository import DishRepository
from app.services.meal_plan_service import MealPlanService


class FakeDishRepository:
    """
    Fake dish repository.
    """

    def list(self):
        return [
            DishORM(
                id="dish-1",
                name="Pilaf",
                recipe_id="recipe-1",
            ),
            DishORM(
                id="dish-2",
                name="Soup",
                recipe_id="recipe-2",
            ),
        ]


class FakeMealPlanRepository:
    """
    Fake persistence repository.
    """

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

    def get_with_details(
        self,
        meal_plan_id: str,
    ):
        return self.meal_plan


def test_generate_and_save_meal_plan():
    meal_plan_repository = FakeMealPlanRepository()

    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        meal_plan_repository=meal_plan_repository,
    )

    result = service.generate_and_save(
        name="Altai Trip",
        participants=10,
        days=2,
        meals_per_day=[
            "breakfast",
            "dinner",
        ],
    )

    assert result.name == "Altai Trip"
    assert result.participants == 10
    assert result.days_count == 2

    assert len(meal_plan_repository.meal_plans) == 1
    assert len(meal_plan_repository.days) == 2
    assert len(meal_plan_repository.items) == 4
    assert len(meal_plan_repository.slots) == 4
    assert len(meal_plan_repository.slot_dishes) == 4

    assert meal_plan_repository.committed is True
