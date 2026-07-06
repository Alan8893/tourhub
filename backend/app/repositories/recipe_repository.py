from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM


class RecipeRepository:

    def __init__(self, session: Session):
        self.session = session

    def get(self, recipe_id: str) -> Optional[RecipeORM]:
        return self.session.get(RecipeORM, recipe_id)

    def list(self) -> List[RecipeORM]:
        return self.session.query(RecipeORM).all()

    def add(self, recipe: RecipeORM) -> None:
        self.session.add(recipe)
        self.session.commit()