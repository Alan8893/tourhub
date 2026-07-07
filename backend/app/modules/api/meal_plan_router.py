from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session

from app.repositories.dish_repository import DishRepository
from app.repositories.meal_plan_repository import MealPlanRepository

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