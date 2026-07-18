from typing import TypedDict

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
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
    RecipeUpdateRequest,
    RecipeWriteResponse,
)
from app.services.recipe_access_service import RecipeAccessService
from app.services.recipe_command_service import RecipeCommandService
from app.services.recipe_query_service import RecipeQueryService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


class RecipeOwnershipPayload(TypedDict):
    scope: RecipeScope
    owner_user_id: int | None
    owner_display_name: str | None
    is_owned_by_current_user: bool
    can_edit: bool
    can_archive: bool
    can_restore: bool
    can_delete: bool


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


def _ownership_response(recipe: RecipeORM, actor: UserORM) -> RecipeOwnershipPayload:
    can_manage = RecipeAccessService.can_manage(recipe, actor)
    return {
        "scope": RecipeScope(recipe.scope),
        "owner_user_id": recipe.owner_user_id,
        "owner_display_name": recipe.owner.display_name if recipe.owner is not None else None,
        "is_owned_by_current_user": recipe.owner_user_id == actor.id,
        "can_edit": RecipeAccessService.can_edit(recipe, actor),
        "can_archive": can_manage and not recipe.is_archived,
        "can_restore": can_manage and recipe.is_archived,
        "can_delete": RecipeAccessService.can_delete(recipe, actor),
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
    service: RecipeQueryService = Depends(get_recipe_query_service),
) -> RecipeListResponse:
    recipes = service.list_recipes(include_archived=include_archived)
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
