from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.meal_slot_repository import MealSlotRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.meal_slot_service import MealSlotService
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/meal-slots", tags=["Meal Slots"])


def get_service() -> MealSlotService:
    return MealSlotService()


def _refresh_purchasing(session: Session, slot) -> None:
    meal_plan = MealPlanRepository(session).get_with_details(
        str(slot.day.meal_plan_id)
    )
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    MealPlanPurchasingRefreshService(
        PurchaseListRepository(session),
        PurchaseChecklistRepository(session),
        MealPlanShoppingService(ShoppingListService(session)),
    ).refresh(meal_plan)


@router.post("/{slot_id}/dishes/{dish_id}")
def add_dish(
    slot_id: str,
    dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
):
    repository = MealSlotRepository(session)
    slot = repository.get(slot_id)

    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")

    item = service.add_dish(slot, dish_id)
    session.add(item)
    session.flush()
    _refresh_purchasing(session, slot)
    session.commit()

    return {
        "id": item.id,
        "dish_id": item.dish_id,
    }


@router.delete("/{slot_id}/dishes/{slot_dish_id}")
def remove_dish(
    slot_id: str,
    slot_dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
):
    repository = MealSlotRepository(session)
    slot = repository.get(slot_id)

    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")

    try:
        service.remove_dish(slot, slot_dish_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    session.flush()
    _refresh_purchasing(session, slot)
    session.commit()

    return {"status": "ok"}


@router.put("/{slot_id}/dishes/{slot_dish_id}/{dish_id}")
def replace_dish(
    slot_id: str,
    slot_dish_id: str,
    dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
):
    repository = MealSlotRepository(session)
    slot = repository.get(slot_id)

    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")

    try:
        item = service.replace_dish(slot, slot_dish_id, dish_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    session.flush()
    _refresh_purchasing(session, slot)
    session.commit()

    return {
        "id": item.id,
        "dish_id": item.dish_id,
    }
