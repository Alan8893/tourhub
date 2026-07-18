from uuid import uuid4

from app.models.dish import DishORM
from app.models.ingredient import IngredientORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.shopping_list_service import ShoppingListService
from tests.conftest import TestingSessionLocal, setup_database


def test_meal_plan_generates_shopping_list():
    setup_database()
    session = TestingSessionLocal()

    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=1000,
    )
    recipe = RecipeORM(
        id=str(uuid4()),
        name="Тестовый плов",
    )
    ingredient = IngredientORM(
        id=str(uuid4()),
        recipe_id=recipe.id,
        product_id=product.id,
        amount_per_person=120,
    )
    dish = DishORM(
        id=str(uuid4()),
        name="Плов",
        recipe_id=recipe.id,
    )
    meal_plan = MealPlanORM(
        id=str(uuid4()),
        name="Алтай",
        participants=10,
        days_count=5,
    )
    day = MealPlanDayORM(
        id=str(uuid4()),
        meal_plan=meal_plan,
        day_number=1,
    )
    item = MealPlanItemORM(
        id=str(uuid4()),
        day=day,
        dish=dish,
        recipe=recipe,
        recipe_id=recipe.id,
        meal_type="dinner",
    )

    session.add_all(
        [
            product,
            recipe,
            ingredient,
            dish,
            meal_plan,
            day,
            item,
        ]
    )
    session.commit()

    service = MealPlanShoppingService(
        shopping_list_service=ShoppingListService(session)
    )
    result = service.calculate(meal_plan)

    assert len(result.items) == 1
    shopping_item = result.items[0]
    assert shopping_item.product_name == "Рис"
    assert shopping_item.amount == 1200
    assert shopping_item.unit == "gram"
