from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.user import UserORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.dish_repository import DishRepository
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.meal_plan import MealPlanResponse
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
) -> MealPlanResponse:
    project = ProjectRepository(session).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    saved = service.generate_and_save_result(
        name=project.name,
        participants=project.participants,
        days=project.days,
        meals_per_day=["breakfast", "snack", "lunch", "dinner"],
        project_id=project.id,
        start_meal=project.first_meal or "breakfast",
        end_meal=project.last_meal or "dinner",
        recipe_generation_mode=project.recipe_generation_mode,
    )
    equipment_service = EquipmentListService(
        EquipmentListRepository(session),
        MealPlanRepository(session),
    )
    try:
        equipment_service.refresh_existing(saved.meal_plan)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return MealPlanMapper.to_response(saved.meal_plan, warnings=saved.warnings)
