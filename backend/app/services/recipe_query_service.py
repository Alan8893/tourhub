from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM


class RecipeQueryService:
    def __init__(self, session: Session):
        self.session = session

    def list_recipes(self) -> list[RecipeORM]:
        statement = (
            select(RecipeORM)
            .options(
                selectinload(RecipeORM.components),
                selectinload(RecipeORM.notes),
            )
            .order_by(RecipeORM.name)
        )
        return list(self.session.scalars(statement).all())

    def get_recipe(self, recipe_id: str) -> RecipeORM:
        statement = (
            select(RecipeORM)
            .where(RecipeORM.id == recipe_id)
            .options(
                selectinload(RecipeORM.components).selectinload(
                    RecipeComponentORM.product
                ),
                selectinload(RecipeORM.notes),
            )
        )
        recipe = self.session.scalar(statement)
        if recipe is None:
            raise ValueError("Recipe not found")
        return recipe
