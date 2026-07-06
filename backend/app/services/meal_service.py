from sqlalchemy.orm import Session

from app.engines.meal_planner import MealPlannerEngine
from app.repositories.dish_repository import DishRepository
from app.repositories.recipe_repository import RecipeRepository


class MealService:
    """
    Application service layer.
    """

    def generate_meal_plan(
        self,
        session: Session,
        dish_ids: list[str],
        days: int,
        participants: int
    ):
        # repositories
        dish_repo = DishRepository(session)
        recipe_repo = RecipeRepository(session)

        # load data
        dishes = {d.id: d for d in dish_repo.list()}
        recipes = {r.id: r for r in recipe_repo.list()}

        # engine
        engine = MealPlannerEngine(recipes=recipes, dishes=dishes)

        return engine.generate_meal_plan(
            dish_ids=dish_ids,
            days=days,
            participants=participants
        )