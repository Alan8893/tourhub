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
from app.core.database import get_db

from app.modules.api.meal_plan_router import get_meal_plan_service
from app.services.meal_plan_service import MealPlanService


DISH_1_ID = "550e8400-e29b-41d4-a716-446655440001"
DISH_2_ID = "550e8400-e29b-41d4-a716-446655440002"
DISH_3_ID = "550e8400-e29b-41d4-a716-446655440003"
RECIPE_1_ID = "660e8400-e29b-41d4-a716-446655440001"
RECIPE_2_ID = "660e8400-e29b-41d4-a716-446655440002"
RECIPE_3_ID = "660e8400-e29b-41d4-a716-446655440003"


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
            DishORM(id=DISH_1_ID, name="Pilaf", recipe_id=RECIPE_1_ID),
            DishORM(id=DISH_2_ID, name="Soup", recipe_id=RECIPE_2_ID),
            DishORM(id=DISH_3_ID, name="Oatmeal", recipe_id=RECIPE_3_ID),
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
    app.dependency_overrides[get_db] = override_session
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
    app.dependency_overrides[get_db] = override_session
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
