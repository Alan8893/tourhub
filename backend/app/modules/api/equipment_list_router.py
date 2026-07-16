from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.equipment_list import EquipmentListORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.equipment import EquipmentListItemResponse, EquipmentListResponse
from app.services.equipment_list_service import EquipmentListService

router = APIRouter(prefix="/equipment-lists", tags=["Equipment"])


def get_service(session: Session = Depends(get_session)) -> EquipmentListService:
    return EquipmentListService(
        EquipmentListRepository(session),
        MealPlanRepository(session),
    )


def _response(equipment_list: EquipmentListORM) -> EquipmentListResponse:
    return EquipmentListResponse(
        id=equipment_list.id,
        project_id=equipment_list.project_id,
        meal_plan_id=equipment_list.meal_plan_id,
        status=equipment_list.status,
        items=[
            EquipmentListItemResponse(
                id=item.id,
                equipment_name=item.equipment_name,
                required_quantity=item.required_quantity,
            )
            for item in equipment_list.items
        ],
    )


@router.get("/project/{project_id}", response_model=EquipmentListResponse)
def get_project_equipment_list(
    project_id: int,
    service: EquipmentListService = Depends(get_service),
) -> EquipmentListResponse:
    equipment_list = service.get_by_project_id(project_id)
    if equipment_list is None:
        raise HTTPException(status_code=404, detail="Equipment list not found")
    return _response(equipment_list)


@router.post("/project/{project_id}/generate", response_model=EquipmentListResponse)
def generate_project_equipment_list(
    project_id: int,
    session: Session = Depends(get_session),
) -> EquipmentListResponse:
    meal_plan_repository = MealPlanRepository(session)
    meal_plan = meal_plan_repository.get_by_project_id(project_id)
    if meal_plan is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    service = EquipmentListService(
        EquipmentListRepository(session),
        meal_plan_repository,
    )
    equipment_list = service.create_from_meal_plan_id(
        str(meal_plan.id),
        project_id=project_id,
    )
    return _response(equipment_list)
