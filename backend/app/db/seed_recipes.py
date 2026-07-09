from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.ingredient import IngredientORM
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM


RECIPES = [
    {
        "name": "Гречневая каша",
        "ingredients": [
            {"product": "Гречка", "amount": 120},
            {"product": "Масло", "amount": 10},
        ],
    },
    {
        "name": "Походный плов",
        "ingredients": [
            {"product": "Рис", "amount": 120},
            {"product": "Мясо", "amount": 100},
            {"product": "Лук", "amount": 30},
            {"product": "Морковь", "amount": 50},
            {"product": "Масло", "amount": 10},
        ],
    },
    {
        "name": "Картофельный суп",
        "ingredients": [
            {"product": "Картофель", "amount": 200},
            {"product": "Морковь", "amount": 40},
            {"product": "Лук", "amount": 30},
            {"product": "Мясо", "amount": 80},
        ],
    },
    {
        "name": "Макароны с тушёнкой",
        "ingredients": [
            {"product": "Макароны", "amount": 120},
            {"product": "Тушёнка", "amount": 150},
        ],
    },
    {
        "name": "Походный борщ",
        "ingredients": [
            {"product": "Картофель", "amount": 150},
            {"product": "Морковь", "amount": 30},
            {"product": "Лук", "amount": 30},
            {"product": "Мясо", "amount": 100},
        ],
    },
]


def seed_recipes(session: Session) -> None:
    """
    Create recipes, legacy ingredients and new recipe components.

    The function is idempotent.
    """

    products = {
        product.name: product
        for product in session.query(ProductORM).all()
    }

    for recipe_data in RECIPES:
        existing_recipe = (
            session.query(RecipeORM)
            .filter(RecipeORM.name == recipe_data["name"])
            .first()
        )

        if existing_recipe:
            continue

        recipe = RecipeORM(
            id=str(uuid4()),
            name=recipe_data["name"],
        )

        session.add(recipe)
        session.flush()

        for ingredient_data in recipe_data["ingredients"]:
            product = products.get(ingredient_data["product"])

            if not product:
                raise ValueError(
                    f"Product not found: {ingredient_data['product']}"
                )

            session.add(
                IngredientORM(
                    id=str(uuid4()),
                    recipe_id=recipe.id,
                    product_id=product.id,
                    amount_per_person=ingredient_data["amount"],
                )
            )

            session.add(
                RecipeComponentORM(
                    id=str(uuid4()),
                    recipe_id=recipe.id,
                    product_id=product.id,
                    component_type="base",
                    amount=ingredient_data["amount"],
                    unit="gram",
                    calculation_type="per_person",
                    people_count=1,
                )
            )

    session.commit()
