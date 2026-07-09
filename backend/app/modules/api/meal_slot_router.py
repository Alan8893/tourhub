from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.meal_slot_repository import MealSlotRepository
from app.services.meal_slot_service import MealSlotService


router = APIRouter(prefix="/meal-slots", tags=["Meal Slots"])


def get_service():
    return MealSlotService()


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
    repository.save(slot)

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

    service.remove_dish(slot, slot_dish_id)
    repository.save(slot)

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

    item = service.replace_dish(slot, slot_dish_id, dish_id)
    repository.save(slot)

    return {
        "id": item.id,
        "dish_id": item.dish_id,
    }
