import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.session import get_session

from app.models.dish import DishORM
from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.modules.api.meal_plan_router import (
    get_meal_plan_service,
)
from app.services.meal_plan_service import MealPlanService



class FakeDishRepository:
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
            DishORM(
                id="dish-3",
                name="Oatmeal",
                recipe_id="recipe-3",
            ),
        ]


class FakeMealPlanRepository:
    def __init__(self):
        self.meal_plans = []
        self.days = []
        self.items = []

    def add(self, meal_plan):
        self.meal_plans.append(meal_plan)

    def add_day(self, day):
        self.days.append(day)

    def add_item(self, item):
        self.items.append(item)

    def commit(self):
        pass


@pytest.fixture
def client():
    """
    FastAPI test client.
    """

    yield TestClient(app)


@pytest.fixture
def fake_dish_repository():
    return FakeDishRepository()


@pytest.fixture
def fake_meal_plan_repository():
    return FakeMealPlanRepository()

@pytest.fixture
def override_meal_plan_service(
    fake_dish_repository,
    fake_meal_plan_repository,
):
    def factory():
        return MealPlanService(
            dish_repository=fake_dish_repository,
            meal_plan_repository=fake_meal_plan_repository,
        )

    app.dependency_overrides[
        get_meal_plan_service
    ] = factory

    yield

    app.dependency_overrides.clear()