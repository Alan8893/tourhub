from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM


class RecipeNoteService:
    def __init__(self, session: Session):
        self.session = session

    def _get_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.get(RecipeORM, recipe_id)
        if recipe is None:
            raise LookupError(f"Recipe not found: {recipe_id}")
        return recipe

    def _get_note(self, recipe_id: str, note_id: str) -> RecipeNoteORM:
        note = self.session.scalar(
            select(RecipeNoteORM).where(
                RecipeNoteORM.id == note_id,
                RecipeNoteORM.recipe_id == recipe_id,
            )
        )
        if note is None:
            raise LookupError(f"Recipe note not found: {note_id}")
        return note

    def get_by_recipe_id(self, recipe_id: str) -> list[RecipeNoteORM]:
        self._get_recipe(recipe_id)
        return list(
            self.session.scalars(
                select(RecipeNoteORM)
                .where(RecipeNoteORM.recipe_id == recipe_id)
                .order_by(RecipeNoteORM.priority, RecipeNoteORM.created_at)
            ).all()
        )

    def create(
        self,
        recipe_id: str,
        note_type: str,
        text: str,
        priority: int,
    ) -> RecipeNoteORM:
        self._get_recipe(recipe_id)
        note = RecipeNoteORM(
            id=str(uuid4()),
            recipe_id=recipe_id,
            type=note_type,
            text=text.strip(),
            priority=priority,
            created_at=datetime.now(UTC),
        )
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def update(
        self,
        recipe_id: str,
        note_id: str,
        note_type: str,
        text: str,
        priority: int,
    ) -> RecipeNoteORM:
        note = self._get_note(recipe_id, note_id)
        note.type = note_type
        note.text = text.strip()
        note.priority = priority
        self.session.commit()
        self.session.refresh(note)
        return note

    def delete(self, recipe_id: str, note_id: str) -> None:
        note = self._get_note(recipe_id, note_id)
        self.session.delete(note)
        self.session.commit()
