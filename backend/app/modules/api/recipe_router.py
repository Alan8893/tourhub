from typing import Literal, TypedDict

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.schemas.recipe import (
    RecipeComponentResponse,
    RecipeComponentWriteRequest,
    RecipeCreateRequest,
    RecipeDetailNoteResponse,
    RecipeDetailResponse,
    RecipeListItemResponse,
    RecipeListResponse,
    RecipeProductResponse,
    RecipeRejectRequest,
    RecipeUpdateRequest,
    RecipeWriteResponse,
)
from app.services.recipe_access_service import RecipeAccessService
from app.services.recipe_command_service import RecipeCommandService
from app.services.recipe_lifecycle_service import RecipeLifecycleService
from app.services.recipe_query_service import RecipeQueryService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


class RecipeOwnershipPayload(TypedDict):
    scope: RecipeScope
    owner_user_id: int | None
    owner_display_name: str | None
    is_owned_by_current_user: bool
    lifecycle_status: RecipeLifecycleStatus
    submitted_by_user_id: int | None
    submitted_by_display_name: str | None
    submitted_at: str | None
    reviewed_by_user_id: int | None
    reviewed_by_display_name: str | None
    reviewed_at: str | None
    review_comment: str | None
    can_edit: bool
    can_archive: bool
    can_restore: bool
    can_delete: bool
    can_submit: bool
    can_publish: bool
    can_reject: bool


def get_recipe_query_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeQueryService:
    return RecipeQueryService(session, actor=actor)


def get_recipe_command_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeCommandService:
    return RecipeCommandService(session, actor=actor)


def get_recipe_lifecycle_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> RecipeLifecycleService:
    return RecipeLifecycleService(session, actor=actor)


def _related_display_name(
    related_user: UserORM | None,
    user_id: int | None,
    actor: UserORM,
) -> str | None:
    if related_user is not None:
        return related_user.display_name
    if user_id == actor.id:
        return actor.display_name
    return None


def _ownership_response(recipe: RecipeORM, actor: UserORM) -> RecipeOwnershipPayload:
    can_review = RecipeAccessService.can_review(recipe, actor)
    return {
        "scope": RecipeScope(recipe.scope),
        "owner_user_id": recipe.owner_user_id,
        "owner_display_name": _related_display_name(
            recipe.owner,
            recipe.owner_user_id,
            actor,
        ),
        "is_owned_by_current_user": recipe.owner_user_id == actor.id,
        "lifecycle_status": RecipeLifecycleStatus(recipe.lifecycle_status),
        "submitted_by_user_id": recipe.submitted_by_user_id,
        "submitted_by_display_name": _related_display_name(
            recipe.submitted_by,
            recipe.submitted_by_user_id,
            actor,
        ),
        "submitted_at": recipe.submitted_at.isoformat() if recipe.submitted_at else None,
        "reviewed_by_user_id": recipe.reviewed_by_user_id,
        "reviewed_by_display_name": _related_display_name(
            recipe.reviewed_by,
            recipe.reviewed_by_user_id,
            actor,
        ),
        "reviewed_at": recipe.reviewed_at.isoformat() if recipe.reviewed_at else None,
        "review_comment": recipe.review_comment,
        "can_edit": RecipeAccessService.can_edit(recipe, actor),
        "can_archive": RecipeAccessService.can_archive(recipe, actor),
        "can_restore": RecipeAccessService.can_restore(recipe, actor),
        "can_delete": RecipeAccessService.can_delete(recipe, actor),
        "can_submit": RecipeAccessService.can_submit(recipe, actor),
        "can_publish": can_review,
        "can_reject": can_review,
    }


def _write_response(recipe: RecipeORM, actor: UserORM) -> RecipeWriteResponse:
    return RecipeWriteResponse(
        id=recipe.id,
        name=recipe.name,
        is_archived=recipe.is_archived,
        **_ownership_response(recipe, actor),
    )


def _component_response(component: RecipeComponentORM) -> RecipeComponentResponse:
    return RecipeComponentResponse(
        id=component.id,
        component_type=component.component_type,
        amount=component.amount,
        unit=component.unit,
        calculation_type=component.calculation_type,
        people_count=component.people_count,
        product=RecipeProductResponse(
            id=component.product.id,
            name=component.product.name,
            category=component.product.category,
            unit=component.product.unit,
            package_size=component.product.package_size,
        ),
    )


@router.get("", response_model=RecipeListResponse)
def list_recipes(
    include_archived: bool = Query(default=False),
    view: Literal["library", "moderation"] = Query(default="library"),
    service: RecipeQueryService = Depends(get_recipe_query_service),
) -> RecipeListResponse:
    try:
        recipes = service.list_recipes(include_archived=include_archived, view=view)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    actor = service.actor
    assert actor is not None
    return RecipeListResponse(
        items=[
            RecipeListItemResponse(
                id=recipe.id,
                name=recipe.name,
                is_archived=recipe.is_archived,
                component_count=len(recipe.components),
                note_count=len(recipe.notes),
                **_ownership_response(recipe, actor),
            )
            for recipe in recipes
        ]
    )


@router.post("", response_model=RecipeWriteResponse, status_code=status.HTTP_201_CREATED)
def create_recipe(
    request: RecipeCreateRequest,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.create_recipe(request.name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    actor = service.actor
    assert actor is not None
    return _write_response(recipe, actor)


@router.patch("/{recipe_id}", response_model=RecipeWriteResponse)
def rename_recipe(
    recipe_id: str,
    request: RecipeUpdateRequest,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.rename_recipe(recipe_id, request.name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    actor = service.actor
    assert actor is not None
    return _write_response(recipe, actor)


@router.post("/{recipe_id}/submit", response_model=RecipeWriteResponse)
def submit_recipe(
    recipe_id: str,
    service: RecipeLifecycleService = Depends(get_recipe_lifecycle_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.submit(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _write_response(recipe, service.actor)


@router.post("/{recipe_id}/publish", response_model=RecipeWriteResponse)
def publish_recipe(
    recipe_id: str,
    service: RecipeLifecycleService = Depends(get_recipe_lifecycle_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.publish(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _write_response(recipe, service.actor)


@router.post("/{recipe_id}/reject", response_model=RecipeWriteResponse)
def reject_recipe(
    recipe_id: str,
    request: RecipeRejectRequest,
    service: RecipeLifecycleService = Depends(get_recipe_lifecycle_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.reject(recipe_id, request.comment)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _write_response(recipe, service.actor)


@router.post("/{recipe_id}/archive", response_model=RecipeWriteResponse)
def archive_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.archive_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    actor = service.actor
    assert actor is not None
    return _write_response(recipe, actor)


@router.post("/{recipe_id}/restore", response_model=RecipeWriteResponse)
def restore_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.restore_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    actor = service.actor
    assert actor is not None
    return _write_response(recipe, actor)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> Response:
    try:
        service.delete_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{recipe_id}/components",
    response_model=RecipeComponentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_recipe_component(
    recipe_id: str,
    request: RecipeComponentWriteRequest,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeComponentResponse:
    try:
        component = service.add_component(recipe_id=recipe_id, **request.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _component_response(component)


@router.put("/{recipe_id}/components/{component_id}", response_model=RecipeComponentResponse)
def update_recipe_component(
    recipe_id: str,
    component_id: str,
    request: RecipeComponentWriteRequest,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeComponentResponse:
    try:
        component = service.update_component(
            recipe_id=recipe_id,
            component_id=component_id,
            **request.model_dump(),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _component_response(component)


@router.delete("/{recipe_id}/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe_component(
    recipe_id: str,
    component_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> Response:
    try:
        service.delete_component(recipe_id, component_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{recipe_id}", response_model=RecipeDetailResponse)
def get_recipe(
    recipe_id: str,
    service: RecipeQueryService = Depends(get_recipe_query_service),
) -> RecipeDetailResponse:
    try:
        recipe = service.get_recipe(recipe_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    components = sorted(
        recipe.components,
        key=lambda component: (component.component_type, component.product.name),
    )
    notes = sorted(recipe.notes, key=lambda note: (note.priority, note.created_at))
    actor = service.actor
    assert actor is not None

    return RecipeDetailResponse(
        id=recipe.id,
        name=recipe.name,
        is_archived=recipe.is_archived,
        components=[_component_response(component) for component in components],
        notes=[
            RecipeDetailNoteResponse(
                id=note.id,
                type=note.type,
                text=note.text,
                priority=note.priority,
                created_at=note.created_at.isoformat(),
            )
            for note in notes
        ],
        **_ownership_response(recipe, actor),
    )
