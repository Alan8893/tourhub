from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.schemas.equipment import (
    EquipmentListItemQuantityRequest,
    EquipmentListItemResponse,
    EquipmentListItemWriteRequest,
    EquipmentListResponse,
)
from app.services.equipment_list_service import EquipmentListService

router = APIRouter(prefix="/equipment-lists", tags=["Equipment"])


def get_service(session: Session = Depends(get_session)) -> EquipmentListService:
    return EquipmentListService(
        EquipmentListRepository(session),
        MealPlanRepository(session),
    )


def _item_response(item: EquipmentListItemORM) -> EquipmentListItemResponse:
    calculated = item.calculated_quantity
    return EquipmentListItemResponse(
        id=item.id,
        equipment_name=item.equipment_name,
        required_quantity=item.required_quantity,
        calculated_quantity=calculated,
        is_manual=item.is_manual,
        is_overridden=calculated is not None and item.required_quantity != calculated,
    )


def _response(
    equipment_list: EquipmentListORM,
    service: EquipmentListService,
) -> EquipmentListResponse:
    return EquipmentListResponse(
        id=equipment_list.id,
        project_id=equipment_list.project_id,
        meal_plan_id=equipment_list.meal_plan_id,
        status=equipment_list.status,
        items=[_item_response(item) for item in service.visible_items(equipment_list)],
    )


@router.get("/project/{project_id}", response_model=EquipmentListResponse)
def get_project_equipment_list(
    project_id: int,
    service: EquipmentListService = Depends(get_service),
) -> EquipmentListResponse:
    equipment_list = service.get_by_project_id(project_id)
    if equipment_list is None:
        raise HTTPException(status_code=404, detail="Equipment list not found")
    return _response(equipment_list, service)


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
    return _response(equipment_list, service)


@router.post(
    "/project/{project_id}/items",
    response_model=EquipmentListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_equipment_item(
    project_id: int,
    payload: EquipmentListItemWriteRequest,
    service: EquipmentListService = Depends(get_service),
) -> EquipmentListItemResponse:
    try:
        item = service.add_manual_item(
            project_id,
            payload.equipment_name,
            payload.required_quantity,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _item_response(item)


@router.put(
    "/project/{project_id}/items/{item_id}",
    response_model=EquipmentListItemResponse,
)
def update_project_equipment_item(
    project_id: int,
    item_id: str,
    payload: EquipmentListItemQuantityRequest,
    service: EquipmentListService = Depends(get_service),
) -> EquipmentListItemResponse:
    try:
        item = service.update_item_quantity(
            project_id,
            item_id,
            payload.required_quantity,
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _item_response(item)


@router.delete(
    "/project/{project_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_equipment_item(
    project_id: int,
    item_id: str,
    service: EquipmentListService = Depends(get_service),
) -> Response:
    try:
        service.delete_item(project_id, item_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
