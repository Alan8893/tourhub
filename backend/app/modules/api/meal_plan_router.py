from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session

from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.modules.projects.repositories.project_repository import ProjectRepository

from app.services.meal_plan_service import MealPlanService
from app.services.meal_plan_mapper import MealPlanMapper
from app.services.meal_plan_shopping_service import (
    MealPlanShoppingService,
)
from app.services.shopping_list_service import (
    ShoppingListService,
)

from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanGenerateResponse,
    MealPlanResponse,
    ShoppingListItemResponse,
    ShoppingListResponse,
    PackagedShoppingItemResponse,
    PackagedShoppingResponse,
)


router = APIRouter(
    prefix="/meal-plans",
    tags=["Meal Plans"],
)


def get_meal_plan_service(
    session: Session = Depends(get_session),
) -> MealPlanService:
    return MealPlanService(
        dish_repository=DishRepository(session),
        meal_plan_repository=MealPlanRepository(session),
    )


def get_meal_plan_shopping_service(
    session: Session = Depends(get_session),
) -> MealPlanShoppingService:
    return MealPlanShoppingService(
        shopping_list_service=ShoppingListService(
            session
        )
    )


@router.post(
    "/generate",
    response_model=MealPlanGenerateResponse,
)
def generate_meal_plan(
    request: MealPlanGenerateRequest,
    service: MealPlanService = Depends(
        get_meal_plan_service
    ),
    shopping_service: MealPlanShoppingService = Depends(
        get_meal_plan_shopping_service
    ),
):
    meal_plan = service.generate_and_save(
        name=request.name,
        participants=request.participants,
        days=request.days,
        meals_per_day=request.meals_per_day,
    )

    shopping_list = shopping_service.calculate(
        meal_plan
    )

    packaged_list = shopping_service.calculate_packaged(
        meal_plan
    )

    return {
        "meal_plan": MealPlanMapper.to_response(
            meal_plan
        ),
        "shopping_list": ShoppingListResponse(
            items=[
                ShoppingListItemResponse(
                    product_name=item.product_name,
                    amount=item.amount,
                    unit=item.unit,
                )
                for item in shopping_list.items
            ]
        ),
        "purchase_list": PackagedShoppingResponse(
            items=[
                PackagedShoppingItemResponse(
                    product_name=item.product_name,
                    amount=item.amount,
                    unit=item.unit,
                    package_size=item.package_size,
                    packages=item.packages,
                )
                for item in packaged_list.items
            ]
        ),
    }


@router.get(
    "/project/{project_id}",
    response_model=MealPlanResponse,
)
def get_project_meal_plan(
    project_id: int,
    session: Session = Depends(get_session),
):
    meal_plan = MealPlanRepository(session).get_by_project_id(
        project_id
    )

    if meal_plan is None:
        raise HTTPException(
            status_code=404,
            detail="Meal plan not found for project",
        )

    return MealPlanMapper.to_response(meal_plan)


@router.post(
    "/project/{project_id}/generate",
    response_model=MealPlanResponse,
)
def generate_project_meal_plan(
    project_id: int,
    service: MealPlanService = Depends(
        get_meal_plan_service
    ),
    session: Session = Depends(get_session),
):
    project = ProjectRepository(session).get_by_id(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    meal_plan = service.generate_and_save(
        name=project.name,
        participants=project.participants,
        days=project.days,
        meals_per_day=["breakfast", "lunch", "dinner"],
        project_id=project.id,
    )

    return MealPlanMapper.to_response(meal_plan)
