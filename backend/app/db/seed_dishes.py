from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.dish import DishORM
from app.models.recipe import RecipeORM


DISHES = [
    {
        "name": "Гречневая каша на завтрак",
        "recipe": "Гречневая каша",
    },
    {
        "name": "Походный плов на ужин",
        "recipe": "Походный плов",
    },
    {
        "name": "Картофельный суп на обед",
        "recipe": "Картофельный суп",
    },
    {
        "name": "Макароны с тушёнкой",
        "recipe": "Макароны с тушёнкой",
    },
    {
        "name": "Борщ походный",
        "recipe": "Походный борщ",
    },
]


def seed_dishes(session: Session) -> None:
    """
    Create dishes linked to recipes.

    The function is idempotent.
    """

    recipes = {
        recipe.name: recipe
        for recipe in session.query(RecipeORM).all()
    }

    for dish_data in DISHES:

        existing_dish = (
            session.query(DishORM)
            .filter(
                DishORM.name == dish_data["name"]
            )
            .first()
        )

        if existing_dish:
            continue

        recipe = recipes.get(
            dish_data["recipe"]
        )

        if not recipe:
            raise ValueError(
                f"Recipe not found: {dish_data['recipe']}"
            )

        dish = DishORM(
            id=str(uuid4()),
            name=dish_data["name"],
            recipe_id=recipe.id,
        )

        session.add(dish)

    session.commit()