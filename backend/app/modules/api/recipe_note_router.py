from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.recipe_note import RecipeNoteORM
from app.models.user import UserORM
from app.schemas.recipe_note import (
    RecipeNoteCreateRequest,
    RecipeNoteListResponse,
    RecipeNoteResponse,
    RecipeNoteWriteRequest,
)
from app.services.recipe_note_service import RecipeNoteService

router = APIRouter(prefix="/recipes/{recipe_id}/notes", tags=["Recipe Notes"])


def get_recipe_note_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeNoteService:
    return RecipeNoteService(session, actor=actor)


def _response(note: RecipeNoteORM) -> RecipeNoteResponse:
    return RecipeNoteResponse(
        id=note.id,
        recipe_id=note.recipe_id,
        type=note.type,
        text=note.text,
        priority=note.priority,
        created_at=note.created_at.isoformat(),
    )


@router.get("", response_model=RecipeNoteListResponse)
def get_recipe_notes(
    recipe_id: str,
    service: RecipeNoteService = Depends(get_recipe_note_service),
) -> RecipeNoteListResponse:
    try:
        notes = service.get_by_recipe_id(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RecipeNoteListResponse(items=[_response(note) for note in notes])


@router.post("", response_model=RecipeNoteResponse, status_code=status.HTTP_201_CREATED)
def create_recipe_note(
    recipe_id: str,
    request: RecipeNoteCreateRequest,
    service: RecipeNoteService = Depends(get_recipe_note_service),
) -> RecipeNoteResponse:
    try:
        note = service.create(
            recipe_id=recipe_id,
            note_type=request.type.value,
            text=request.text,
            priority=request.priority,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _response(note)


@router.put("/{note_id}", response_model=RecipeNoteResponse)
def update_recipe_note(
    recipe_id: str,
    note_id: str,
    request: RecipeNoteWriteRequest,
    service: RecipeNoteService = Depends(get_recipe_note_service),
) -> RecipeNoteResponse:
    try:
        note = service.update(
            recipe_id=recipe_id,
            note_id=note_id,
            note_type=request.type.value,
            text=request.text,
            priority=request.priority,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _response(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_note(
    recipe_id: str,
    note_id: str,
    service: RecipeNoteService = Depends(get_recipe_note_service),
) -> Response:
    try:
        service.delete(recipe_id, note_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
