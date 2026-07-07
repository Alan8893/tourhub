import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import (
    Base,
    ProductORM,
    IngredientORM,
    RecipeORM,
    DishORM,
    MealPlanORM,
    MealPlanDayORM,
    MealPlanItemORM,
    PurchaseChecklistORM,
    PurchaseChecklistItemORM,
    PurchaseListORM,
    PurchaseListItemORM,
)
from app.core.session import get_session

from app.modules.api.meal_plan_router import get_meal_plan_service
from app.services.meal_plan_service import MealPlanService


test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


def setup_database():
    Base.metadata.create_all(bind=test_engine)


class FakeDishRepository:
    def list(self):
        return [
            DishORM(id="dish-1", name="Pilaf", recipe_id="recipe-1"),
            DishORM(id="dish-2", name="Soup", recipe_id="recipe-2"),
            DishORM(id="dish-3", name="Oatmeal", recipe_id="recipe-3"),
        ]


class FakeMealPlanRepository:
    def __init__(self):
        self.meal_plans = []
        self.days = []
        self.items = []
        self.meal_plan = None

    def add(self, meal_plan):
        self.meal_plans.append(meal_plan)
        self.meal_plan = meal_plan

    def add_day(self, day):
        self.days.append(day)

    def add_item(self, item):
        self.items.append(item)

    def commit(self):
        pass

    def get_with_details(self, meal_plan_id: str):
        return self.meal_plan


@pytest.fixture
def client():
    setup_database()
    app.dependency_overrides[get_session] = override_session
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def override_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def fake_dish_repository():
    return FakeDishRepository()


@pytest.fixture
def fake_meal_plan_repository():
    return FakeMealPlanRepository()


@pytest.fixture
def db_session():
    setup_database()
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def override_database_session():
    setup_database()
    app.dependency_overrides[get_session] = override_session
    yield
    app.dependency_overrides.clear()


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

    app.dependency_overrides[get_meal_plan_service] = factory
    yield
    app.dependency_overrides.clear()
