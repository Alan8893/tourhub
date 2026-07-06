from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.schemas.meal_plan import MealPlanRequest, MealPlanResponse
from app.services.meal_service import MealService


router = APIRouter(prefix="/meal-plan", tags=["Meal Plan"])


@router.post("/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    payload: MealPlanRequest,
    session: Session = Depends(get_session)
):
    service = MealService()

    return service.generate_meal_plan(
        session=session,
        dish_ids=payload.dish_ids,
        days=payload.days,
        participants=payload.participants
    )