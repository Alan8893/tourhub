from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.schemas.purchase_checklist import (
    PurchaseChecklistItemResponse,
    PurchaseChecklistItemUpdate,
    PurchaseChecklistResponse,
)
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
        meal_plan_repository=MealPlanRepository(session),
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
):
    try:
        return service.create_from_meal_plan_id(meal_plan_id)
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


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


@router.patch(
    "/items/{item_id}",
    response_model=PurchaseChecklistItemResponse,
)
def update_purchase_checklist_item(
    item_id: str,
    payload: PurchaseChecklistItemUpdate,
    service: PurchaseChecklistService = Depends(
        get_purchase_checklist_service
    ),
):
    try:
        return service.update_item(
            item_id=item_id,
            checked=payload.is_checked,
            purchased_quantity=payload.purchased_quantity,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
