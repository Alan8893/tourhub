from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM


class RecipeNoteService:
    def __init__(self, session: Session):
        self.session = session

    def get_by_recipe_id(self, recipe_id: str):
        recipe = (
            self.session.query(RecipeORM)
            .filter(RecipeORM.id == recipe_id)
            .first()
        )

        if recipe is None:
            raise ValueError(f"Recipe not found: {recipe_id}")

        return list(recipe.notes)
