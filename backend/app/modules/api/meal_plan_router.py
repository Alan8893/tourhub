from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session

from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository

from app.services.meal_plan_service import MealPlanService
from app.services.meal_plan_mapper import MealPlanMapper

from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanResponse,
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


@router.post(
    "/generate",
    response_model=MealPlanResponse,
)
def generate_meal_plan(
    request: MealPlanGenerateRequest,
    service: MealPlanService = Depends(
        get_meal_plan_service
    ),
):
    meal_plan = service.generate_and_save(
        name=request.name,
        participants=request.participants,
        days=request.days,
        meals_per_day=request.meals_per_day,
    )

    return MealPlanMapper.to_response(
        meal_plan
    )