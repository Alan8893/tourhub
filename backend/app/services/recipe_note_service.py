from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM


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

    def create(
        self,
        recipe_id: str,
        note_type: str,
        text: str,
        priority: int,
    ) -> RecipeNoteORM:
        recipe = (
            self.session.query(RecipeORM)
            .filter(RecipeORM.id == recipe_id)
            .first()
        )

        if recipe is None:
            raise ValueError(f"Recipe not found: {recipe_id}")

        note = RecipeNoteORM(
            id=str(uuid4()),
            recipe_id=recipe_id,
            type=note_type,
            text=text,
            priority=priority,
            created_at=datetime.now(timezone.utc),
        )

        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note
