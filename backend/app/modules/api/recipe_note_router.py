from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.schemas.recipe_note import (
    RecipeNoteCreateRequest,
    RecipeNoteListResponse,
    RecipeNoteResponse,
)
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
                type=note.type,
                text=note.text,
                priority=note.priority,
                created_at=note.created_at.isoformat(),
            )
            for note in notes
        ]
    )


@router.post("", response_model=RecipeNoteResponse, status_code=status.HTTP_201_CREATED)
def create_recipe_note(
    recipe_id: str,
    request: RecipeNoteCreateRequest,
    service: RecipeNoteService = Depends(get_recipe_note_service),
):
    try:
        note = service.create(
            recipe_id=recipe_id,
            note_type=request.type,
            text=request.text,
            priority=request.priority,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return RecipeNoteResponse(
        id=note.id,
        recipe_id=note.recipe_id,
        type=note.type,
        text=note.text,
        priority=note.priority,
        created_at=note.created_at.isoformat(),
    )
