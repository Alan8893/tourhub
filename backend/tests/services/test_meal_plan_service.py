from app.engines.meal_plan_generator import MealPlanGenerator
from app.models.dish import DishORM
from app.repositories.dish_repository import DishRepository
from app.services.meal_plan_service import MealPlanService


class FakeDishRepository:
    """
    Fake repository for service unit test.
    """

    def list(self):
        return [
            DishORM(
                id="1",
                name="Pilaf",
                recipe_id="recipe-1",
            ),
            DishORM(
                id="2",
                name="Soup",
                recipe_id="recipe-2",
            ),
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

    assert result.items[1].meal_type == "dinner"

    assert result.items[0].dish_name == "Pilaf"