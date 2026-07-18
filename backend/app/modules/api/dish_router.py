from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.dish import DishORM
from app.models.recipe import RecipeORM
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.modules.domain.meal_role import MEAL_ROLE_ORDER, MealRole
from app.modules.domain.meal_type import MEAL_TYPE_ORDER, MealType
from app.schemas.dish import (
    DishCatalogueCoverageResponse,
    DishCatalogueReadinessResponse,
    DishCreateRequest,
    DishListResponse,
    DishMealRoleResponse,
    DishMealRolesUpdateRequest,
    DishRecipeResponse,
    DishResponse,
    DishUpdateRequest,
)
from app.services.dish_catalogue_readiness_service import (
    DishCatalogueReadinessService,
)
from app.services.dish_service import DishService

router = APIRouter(prefix="/dishes", tags=["Dishes"])
_MEAL_ROLE_POSITION = {
    role.value: position for position, role in enumerate(MEAL_ROLE_ORDER)
}
_MEAL_TYPE_POSITION = {
    meal_type.value: position for position, meal_type in enumerate(MEAL_TYPE_ORDER)
}


def get_dish_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> DishService:
    return DishService(session, actor=actor)


def get_dish_catalogue_readiness_service(
    session: Session = Depends(get_session),
) -> DishCatalogueReadinessService:
    return DishCatalogueReadinessService(session)


def _recipe_response(
    recipe: RecipeORM,
    *,
    default_recipe_id: str,
) -> DishRecipeResponse:
    return DishRecipeResponse(
        id=recipe.id,
        name=recipe.name,
        is_archived=recipe.is_archived,
        scope=RecipeScope(recipe.scope),
        owner_display_name=recipe.owner.display_name if recipe.owner is not None else None,
        is_default=recipe.id == default_recipe_id,
    )


def _dish_response(dish: DishORM, service: DishService) -> DishResponse:
    meal_roles = sorted(
        dish.meal_roles,
        key=lambda assignment: _MEAL_ROLE_POSITION[assignment.role],
    )
    variants = service.visible_variants(dish)
    return DishResponse(
        id=dish.id,
        name=dish.name,
        recipe=_recipe_response(dish.recipe, default_recipe_id=dish.recipe_id),
        recipes=[
            _recipe_response(recipe, default_recipe_id=dish.recipe_id)
            for recipe in variants
        ],
        meal_roles=[
            DishMealRoleResponse(
                role=MealRole(assignment.role),
                is_repeatable=assignment.is_repeatable,
                allowed_meal_types=[
                    MealType(meal_type.meal_type)
                    for meal_type in sorted(
                        assignment.meal_types,
                        key=lambda item: _MEAL_TYPE_POSITION[item.meal_type],
                    )
                ],
            )
            for assignment in meal_roles
        ],
    )


@router.get("", response_model=DishListResponse)
def list_dishes(service: DishService = Depends(get_dish_service)) -> DishListResponse:
    return DishListResponse(
        items=[_dish_response(dish, service) for dish in service.list_dishes()]
    )


@router.get(
    "/catalogue-readiness",
    response_model=DishCatalogueReadinessResponse,
)
def get_dish_catalogue_readiness(
    service: DishCatalogueReadinessService = Depends(
        get_dish_catalogue_readiness_service
    ),
) -> DishCatalogueReadinessResponse:
    readiness = service.evaluate()
    return DishCatalogueReadinessResponse(
        ready=readiness.ready,
        active_dish_count=readiness.active_dish_count,
        classified_dish_count=readiness.classified_dish_count,
        unclassified_dish_count=readiness.unclassified_dish_count,
        coverage=[
            DishCatalogueCoverageResponse(
                meal_type=item.meal_type,
                role=item.role,
                required=item.required,
                candidate_count=item.candidate_count,
                minimum_required=item.minimum_required,
                ready=item.ready,
            )
            for item in readiness.coverage
        ],
    )


@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: str,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        return _dish_response(service.get_dish(dish_id), service)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    request: DishCreateRequest,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        dish = service.create_dish(request.name, request.recipe_id, request.recipe_ids)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if "unique" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _dish_response(dish, service)


@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: str,
    request: DishUpdateRequest,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        dish = service.update_dish(
            dish_id,
            request.name,
            request.recipe_id,
            request.recipe_ids,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if "unique" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _dish_response(dish, service)


@router.put("/{dish_id}/meal-roles", response_model=DishResponse)
def replace_dish_meal_roles(
    dish_id: str,
    request: DishMealRolesUpdateRequest,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        dish = service.replace_meal_roles(
            dish_id,
            [
                (
                    assignment.role.value,
                    assignment.is_repeatable,
                    [meal_type.value for meal_type in assignment.allowed_meal_types],
                )
                for assignment in request.roles
            ],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _dish_response(dish, service)
