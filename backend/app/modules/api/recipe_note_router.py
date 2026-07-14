from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.recipe_note_type import RecipeNoteType
from app.schemas.recipe_note import RecipeNoteListResponse, RecipeNoteResponse
from app.services.recipe_note_service import RecipeNoteService


router = APIRouter(prefix="/recipes/{recipe_id}/notes", tags=["Recipe Notes"])


def get_recipe_note_service(session: Session = Depends(get_session)):
    return RecipeNoteService(session)


@router.get("", response_model=RecipeNoteListResponse)
def get_recipe_notes(
    recipe_id: str,
    service: RecipeNoteService = Depends(get_recipe_note_service),
):
    try:
        notes = service.get_by_recipe_id(recipe_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RecipeNoteListResponse(
        items=[
            RecipeNoteResponse(
                id=note.id,
                recipe_id=note.recipe_id,
                type=RecipeNoteType(note.type).value,
                text=note.text,
                priority=note.priority,
                created_at=note.created_at.isoformat(),
            )
            for note in notes
        ]
    )
