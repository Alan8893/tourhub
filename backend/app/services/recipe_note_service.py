from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM
from app.models.user import UserORM
from app.services.recipe_access_service import RecipeAccessService


class RecipeNoteService:
    def __init__(self, session: Session, actor: UserORM | None = None):
        self.session = session
        self.actor = actor

    def _get_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.get(RecipeORM, recipe_id)
        if recipe is None:
            raise LookupError(f"Recipe not found: {recipe_id}")
        return RecipeAccessService.require_visible(recipe, self.actor)

    def _get_editable_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_recipe(recipe_id)
        return RecipeAccessService.require_editable(recipe, self.actor)

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
        self._get_editable_recipe(recipe_id)
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
        self._get_editable_recipe(recipe_id)
        note = self._get_note(recipe_id, note_id)
        note.type = note_type
        note.text = text.strip()
        note.priority = priority
        self.session.commit()
        self.session.refresh(note)
        return note

    def delete(self, recipe_id: str, note_id: str) -> None:
        self._get_editable_recipe(recipe_id)
        note = self._get_note(recipe_id, note_id)
        self.session.delete(note)
        self.session.commit()
