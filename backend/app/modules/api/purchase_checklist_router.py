from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import (
    PurchaseChecklistRepository,
)
from app.schemas.purchase_checklist import PurchaseChecklistResponse
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.shopping_list_service import ShoppingListService


router = APIRouter(
    prefix="/purchase-checklists",
    tags=["Purchase Checklists"],
)


def get_purchase_checklist_service(
    session: Session = Depends(get_session),
) -> PurchaseChecklistService:
    return PurchaseChecklistService(
        repository=PurchaseChecklistRepository(session),
        shopping_service=MealPlanShoppingService(
            shopping_list_service=ShoppingListService(session)
        ),
    )


@router.post(
    "/from-meal-plan/{meal_plan_id}",
    response_model=PurchaseChecklistResponse,
)
def create_purchase_checklist(
    meal_plan_id: str,
    service: PurchaseChecklistService = Depends(
        get_purchase_checklist_service
    ),
    session: Session = Depends(get_session),
):
    meal_plan = MealPlanRepository(session).get_with_details(
        meal_plan_id
    )

    if not meal_plan:
        raise HTTPException(
            status_code=404,
            detail="Meal plan not found",
        )

    return service.create_from_meal_plan(meal_plan)


@router.get(
    "/{checklist_id}",
    response_model=PurchaseChecklistResponse,
)
def get_purchase_checklist(
    checklist_id: str,
    service: PurchaseChecklistService = Depends(
        get_purchase_checklist_service
    ),
):
    checklist = service.get(checklist_id)

    if not checklist:
        raise HTTPException(
            status_code=404,
            detail="Purchase checklist not found",
        )

    return checklist
