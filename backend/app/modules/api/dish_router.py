from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.dish import DishORM
from app.modules.domain.meal_role import MEAL_ROLE_ORDER, MealRole
from app.schemas.dish import (
    DishCreateRequest,
    DishListResponse,
    DishMealRoleResponse,
    DishMealRolesUpdateRequest,
    DishRecipeResponse,
    DishResponse,
    DishUpdateRequest,
)
from app.services.dish_service import DishService

router = APIRouter(prefix="/dishes", tags=["Dishes"])
_MEAL_ROLE_POSITION = {
    role.value: position for position, role in enumerate(MEAL_ROLE_ORDER)
}


def get_dish_service(session: Session = Depends(get_session)) -> DishService:
    return DishService(session)


def _dish_response(dish: DishORM) -> DishResponse:
    meal_roles = sorted(
        dish.meal_roles,
        key=lambda assignment: _MEAL_ROLE_POSITION[assignment.role],
    )
    return DishResponse(
        id=dish.id,
        name=dish.name,
        recipe=DishRecipeResponse(
            id=dish.recipe.id,
            name=dish.recipe.name,
            is_archived=dish.recipe.is_archived,
        ),
        meal_roles=[
            DishMealRoleResponse(
                role=MealRole(assignment.role),
                is_repeatable=assignment.is_repeatable,
            )
            for assignment in meal_roles
        ],
    )


@router.get("", response_model=DishListResponse)
def list_dishes(service: DishService = Depends(get_dish_service)) -> DishListResponse:
    return DishListResponse(items=[_dish_response(dish) for dish in service.list_dishes()])


@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: str,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        return _dish_response(service.get_dish(dish_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    request: DishCreateRequest,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        dish = service.create_dish(request.name, request.recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if "unique" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _dish_response(dish)


@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: str,
    request: DishUpdateRequest,
    service: DishService = Depends(get_dish_service),
) -> DishResponse:
    try:
        dish = service.update_dish(dish_id, request.name, request.recipe_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if "unique" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return _dish_response(dish)


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
                (assignment.role.value, assignment.is_repeatable)
                for assignment in request.roles
            ],
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _dish_response(dish)
