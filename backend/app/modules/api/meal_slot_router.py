from collections.abc import Callable
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.project_access import ProjectAccessPolicy
from app.core.session import get_session
from app.models.dish import DishORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.user import UserORM
from app.repositories.dish_repository import DishRepository
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.meal_slot_repository import MealSlotRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.audit_service import AuditService
from app.services.dish_recipe_variant_service import DishRecipeVariantService
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_derived_refresh_service import MealPlanDerivedRefreshService
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.meal_slot_service import MealSlotService
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/meal-slots", tags=["Meal Slots"])


def get_service() -> MealSlotService:
    return MealSlotService()


def _get_selectable_dish_and_recipe(
    session: Session,
    slot: MealSlotORM,
    dish_id: str,
    actor: UserORM,
) -> tuple[DishORM, RecipeORM]:
    dish = DishRepository(session).get(dish_id)
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    project = slot.day.meal_plan.project
    mode = (
        project.recipe_generation_mode
        if project is not None
        else RecipeGenerationMode.CLUB_ONLY.value
    )
    recipes = DishRecipeVariantService.ordered_for_generation(dish, actor, mode)
    if not recipes:
        raise HTTPException(
            status_code=422,
            detail="Dish has no recipe available for the project generation mode",
        )
    return dish, recipes[0]


def _refresh_derived_data(session: Session, slot: MealSlotORM) -> None:
    meal_plan_repository = MealPlanRepository(session)
    meal_plan = meal_plan_repository.get_with_details(str(slot.day.meal_plan_id))
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    MealPlanDerivedRefreshService(
        MealPlanPurchasingRefreshService(
            PurchaseListRepository(session),
            PurchaseChecklistRepository(session),
            MealPlanShoppingService(ShoppingListService(session)),
        ),
        EquipmentListService(
            EquipmentListRepository(session),
            meal_plan_repository,
        ),
    ).refresh(meal_plan)


def _slot_snapshot(slot: MealSlotORM) -> dict[str, object]:
    dishes = cast(list[MealSlotDishORM], slot.dishes)
    return {
        "meal_plan_id": str(slot.day.meal_plan_id),
        "project_id": slot.day.meal_plan.project_id,
        "day_number": slot.day.day_number,
        "meal_type": slot.meal_type,
        "is_manually_edited": slot.is_manually_edited,
        "dishes": [
            {
                "slot_dish_id": item.id,
                "dish_id": item.dish_id,
                "recipe_id": item.recipe_id,
                "order": item.order,
            }
            for item in dishes[:20]
        ],
        "dish_count": len(dishes),
    }


def _slot_context(slot: MealSlotORM) -> dict[str, object]:
    return {
        "meal_plan_id": str(slot.day.meal_plan_id),
        "project_id": slot.day.meal_plan.project_id,
        "day_number": slot.day.day_number,
        "meal_type": slot.meal_type,
    }


def _require_slot_menu_write(
    session: Session,
    slot: MealSlotORM,
    actor: UserORM,
) -> None:
    project_id = slot.day.meal_plan.project_id
    if project_id is None:
        raise HTTPException(status_code=404, detail="Project not found")
    ProjectAccessPolicy.require_menu_write(session, project_id, actor)


def _commit_recalculation(
    session: Session,
    operation: Callable[[], dict[str, str]],
) -> dict[str, str]:
    try:
        result = operation()
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise


@router.post("/{slot_id}/dishes/{dish_id}")
def add_dish(
    slot_id: str,
    dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
    actor: UserORM = Depends(require_preparation_access),
) -> dict[str, str]:
    slot = MealSlotRepository(session).get(slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")
    _require_slot_menu_write(session, slot, actor)
    before = _slot_snapshot(slot)

    def operation() -> dict[str, str]:
        dish, recipe = _get_selectable_dish_and_recipe(session, slot, dish_id, actor)
        item = service.add_dish(slot, dish.id, recipe.id)
        session.add(item)
        session.flush()
        _refresh_derived_data(session, slot)
        AuditService(session).record(
            actor=actor,
            action="meal_slot_dish_added",
            entity_type="meal_slot",
            entity_id=slot.id,
            before=before,
            after=_slot_snapshot(slot),
            context={
                **_slot_context(slot),
                "slot_dish_id": item.id,
                "dish_id": dish.id,
                "dish_name": dish.name,
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
            },
        )
        return {"id": item.id, "dish_id": item.dish_id, "recipe_id": item.recipe_id}

    return _commit_recalculation(session, operation)


@router.delete("/{slot_id}/dishes/{slot_dish_id}")
def remove_dish(
    slot_id: str,
    slot_dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
    actor: UserORM = Depends(require_preparation_access),
) -> dict[str, str]:
    slot = MealSlotRepository(session).get(slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")
    _require_slot_menu_write(session, slot, actor)
    before = _slot_snapshot(slot)

    def operation() -> dict[str, str]:
        removed = next(
            (
                item
                for item in cast(list[MealSlotDishORM], slot.dishes)
                if item.id == slot_dish_id
            ),
            None,
        )
        try:
            service.remove_dish(slot, slot_dish_id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        session.flush()
        _refresh_derived_data(session, slot)
        AuditService(session).record(
            actor=actor,
            action="meal_slot_dish_removed",
            entity_type="meal_slot",
            entity_id=slot.id,
            before=before,
            after=_slot_snapshot(slot),
            context={
                **_slot_context(slot),
                "slot_dish_id": slot_dish_id,
                "dish_id": removed.dish_id if removed is not None else None,
                "recipe_id": removed.recipe_id if removed is not None else None,
            },
        )
        return {"status": "ok"}

    return _commit_recalculation(session, operation)


@router.put("/{slot_id}/dishes/{slot_dish_id}/{dish_id}")
def replace_dish(
    slot_id: str,
    slot_dish_id: str,
    dish_id: str,
    session: Session = Depends(get_session),
    service: MealSlotService = Depends(get_service),
    actor: UserORM = Depends(require_preparation_access),
) -> dict[str, str]:
    slot = MealSlotRepository(session).get(slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Meal slot not found")
    _require_slot_menu_write(session, slot, actor)
    before = _slot_snapshot(slot)

    def operation() -> dict[str, str]:
        previous = next(
            (
                item
                for item in cast(list[MealSlotDishORM], slot.dishes)
                if item.id == slot_dish_id
            ),
            None,
        )
        previous_dish_id = previous.dish_id if previous is not None else None
        previous_recipe_id = previous.recipe_id if previous is not None else None
        dish, recipe = _get_selectable_dish_and_recipe(session, slot, dish_id, actor)
        try:
            item = service.replace_dish(slot, slot_dish_id, dish.id, recipe.id)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        session.flush()
        _refresh_derived_data(session, slot)
        AuditService(session).record(
            actor=actor,
            action="meal_slot_dish_replaced",
            entity_type="meal_slot",
            entity_id=slot.id,
            before=before,
            after=_slot_snapshot(slot),
            context={
                **_slot_context(slot),
                "slot_dish_id": item.id,
                "previous_dish_id": previous_dish_id,
                "previous_recipe_id": previous_recipe_id,
                "dish_id": dish.id,
                "dish_name": dish.name,
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
            },
        )
        return {"id": item.id, "dish_id": item.dish_id, "recipe_id": item.recipe_id}

    return _commit_recalculation(session, operation)
