from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.user import UserORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.dish_repository import DishRepository
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.meal_plan import MealPlanResponse
from app.services.audit_service import AuditService
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_mapper import MealPlanMapper
from app.services.meal_plan_service import MealPlanService

router = APIRouter(prefix="/meal-plans", tags=["Meal Plans"])


def get_meal_plan_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> MealPlanService:
    return MealPlanService(
        dish_repository=DishRepository(session),
        meal_plan_repository=MealPlanRepository(session),
        actor=actor,
    )


def _meal_plan_snapshot(meal_plan: MealPlanORM) -> dict[str, object]:
    days = cast(list[MealPlanDayORM], meal_plan.days)
    slots = [slot for day in days for slot in cast(list[MealSlotORM], day.slots)]
    slot_dishes = [
        item for slot in slots for item in cast(list[MealSlotDishORM], slot.dishes)
    ]
    return {
        "name": meal_plan.name,
        "participants": meal_plan.participants,
        "days_count": meal_plan.days_count,
        "day_count": len(days),
        "slot_count": len(slots),
        "slot_dish_count": len(slot_dishes),
        "manual_slot_count": sum(slot.is_manually_edited for slot in slots),
        "warnings": list(meal_plan.warnings[:20]),
    }


@router.get("/project/{project_id}", response_model=MealPlanResponse)
def get_project_meal_plan(
    project_id: int,
    session: Session = Depends(get_session),
) -> MealPlanResponse:
    meal_plan = MealPlanRepository(session).get_by_project_id(project_id)
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found for project")
    return MealPlanMapper.to_response(meal_plan)


@router.post("/project/{project_id}/generate", response_model=MealPlanResponse)
def generate_project_meal_plan(
    project_id: int,
    service: MealPlanService = Depends(get_meal_plan_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> MealPlanResponse:
    project = ProjectRepository(session).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    meal_plan_repository = MealPlanRepository(session)
    current_plan = meal_plan_repository.get_by_project_id(project_id)
    existing_plan = (
        meal_plan_repository.get_with_details(str(current_plan.id))
        if current_plan is not None
        else None
    )
    before = _meal_plan_snapshot(existing_plan) if existing_plan is not None else None

    try:
        saved = service.generate_and_save_result(
            name=project.name,
            participants=project.participants,
            days=project.days,
            meals_per_day=["breakfast", "snack", "lunch", "dinner"],
            project_id=project.id,
            start_meal=project.first_meal or "breakfast",
            end_meal=project.last_meal or "dinner",
            recipe_generation_mode=project.recipe_generation_mode,
            commit=False,
        )
        equipment_refreshed = (
            EquipmentListService(
                EquipmentListRepository(session),
                meal_plan_repository,
            ).refresh_existing(saved.meal_plan)
            is not None
        )
        AuditService(session).record(
            actor=actor,
            action="meal_plan_generated",
            entity_type="meal_plan",
            entity_id=saved.meal_plan.id,
            before=before,
            after=_meal_plan_snapshot(saved.meal_plan),
            context={
                "project_id": project.id,
                "project_name": project.name,
                "generation_kind": (
                    "regeneration" if existing_plan is not None else "initial"
                ),
                "recipe_generation_mode": project.recipe_generation_mode,
                "preserved_manual_slot_count": (
                    before["manual_slot_count"] if before is not None else 0
                ),
                "equipment_refreshed": equipment_refreshed,
            },
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    return MealPlanMapper.to_response(saved.meal_plan, warnings=saved.warnings)
