from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.schemas.recipe import (
    RecipeComponentResponse,
    RecipeDetailNoteResponse,
    RecipeDetailResponse,
    RecipeListItemResponse,
    RecipeListResponse,
    RecipeProductResponse,
)
from app.services.recipe_query_service import RecipeQueryService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def get_recipe_query_service(
    session: Session = Depends(get_session),
) -> RecipeQueryService:
    return RecipeQueryService(session)


@router.get("", response_model=RecipeListResponse)
def list_recipes(
    service: RecipeQueryService = Depends(get_recipe_query_service),
) -> RecipeListResponse:
    recipes = service.list_recipes()
    return RecipeListResponse(
        items=[
            RecipeListItemResponse(
                id=recipe.id,
                name=recipe.name,
                component_count=len(recipe.components),
                note_count=len(recipe.notes),
            )
            for recipe in recipes
        ]
    )


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
        components=[
            RecipeComponentResponse(
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
            for component in components
        ],
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
