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
        self.committed = False

    def add(self, meal_plan):
        self.meal_plans.append(meal_plan)

    def add_day(self, day):
        self.days.append(day)

    def add_item(self, item):
        self.items.append(item)

    def commit(self):
        self.committed = True


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

    assert meal_plan_repository.committed is True