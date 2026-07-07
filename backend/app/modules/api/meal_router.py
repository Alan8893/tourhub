from fastapi import APIRouter

from app.schemas.meal_plan import (
    MealPlanGenerateRequest,
    MealPlanResponse,
)


router = APIRouter(
    prefix="/meal-plans",
    tags=["Meal Plans"],
)


@router.post(
    "/",
    response_model=MealPlanResponse,
)
def create_meal_plan(
    request: MealPlanGenerateRequest,
):
    """
    Legacy endpoint placeholder.

    Real generation endpoint:
    POST /meal-plans/generate
    """

    raise NotImplementedError(
        "Use POST /meal-plans/generate"
    )