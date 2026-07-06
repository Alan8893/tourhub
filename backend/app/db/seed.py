from sqlalchemy.orm import Session

from app.models.dish import DishORM
from app.models.recipe import RecipeORM


def run_seed(session: Session):
    """
    Seed initial test data for development.
    """

    # -------------------
    # RECIPES
    # -------------------
    recipes = [
        RecipeORM(
            id="r1",
            name="Pasta",
            ingredients={
                "pasta": 100,
                "cheese": 20
            }
        ),
        RecipeORM(
            id="r2",
            name="Soup",
            ingredients={
                "water": 300,
                "potato": 150
            }
        ),
    ]

    # -------------------
    # DISHES
    # -------------------
    dishes = [
        DishORM(
            id="d1",
            name="Pasta Dish",
            recipe_id="r1"
        ),
        DishORM(
            id="d2",
            name="Soup Dish",
            recipe_id="r2"
        ),
    ]

    # -------------------
    # INSERT (idempotent)
    # -------------------
    for recipe in recipes:
        exists = session.get(RecipeORM, recipe.id)
        if not exists:
            session.add(recipe)

    for dish in dishes:
        exists = session.get(DishORM, dish.id)
        if not exists:
            session.add(dish)

    session.commit()