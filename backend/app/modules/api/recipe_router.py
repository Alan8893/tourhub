from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
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
from app.services.recipe_command_service import RecipeCommandService
from app.services.recipe_query_service import RecipeQueryService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def get_recipe_query_service(
    session: Session = Depends(get_session),
) -> RecipeQueryService:
    return RecipeQueryService(session)


def get_recipe_command_service(
    session: Session = Depends(get_session),
) -> RecipeCommandService:
    return RecipeCommandService(session)


def _write_response(recipe: RecipeORM) -> RecipeWriteResponse:
    return RecipeWriteResponse(
        id=recipe.id,
        name=recipe.name,
        is_archived=recipe.is_archived,
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
    return RecipeListResponse(
        items=[
            RecipeListItemResponse(
                id=recipe.id,
                name=recipe.name,
                is_archived=recipe.is_archived,
                component_count=len(recipe.components),
                note_count=len(recipe.notes),
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
    return _write_response(recipe)


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
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _write_response(recipe)


@router.post("/{recipe_id}/archive", response_model=RecipeWriteResponse)
def archive_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.archive_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _write_response(recipe)


@router.post("/{recipe_id}/restore", response_model=RecipeWriteResponse)
def restore_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> RecipeWriteResponse:
    try:
        recipe = service.restore_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _write_response(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: str,
    service: RecipeCommandService = Depends(get_recipe_command_service),
) -> Response:
    try:
        service.delete_recipe(recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
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
    )
