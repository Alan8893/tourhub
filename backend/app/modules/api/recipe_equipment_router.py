from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.schemas.equipment import (
    RecipeEquipmentRequirementListResponse,
    RecipeEquipmentRequirementResponse,
    RecipeEquipmentRequirementWriteRequest,
)
from app.services.recipe_equipment_service import RecipeEquipmentService

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def get_service(session: Session = Depends(get_session)) -> RecipeEquipmentService:
    return RecipeEquipmentService(session)


def _response(
    requirement: RecipeEquipmentRequirementORM,
) -> RecipeEquipmentRequirementResponse:
    return RecipeEquipmentRequirementResponse(
        id=requirement.id,
        recipe_id=requirement.recipe_id,
        equipment_name=requirement.equipment_name,
        quantity=requirement.quantity,
    )


@router.get(
    "/{recipe_id}/equipment-requirements",
    response_model=RecipeEquipmentRequirementListResponse,
)
def list_requirements(
    recipe_id: str,
    service: RecipeEquipmentService = Depends(get_service),
) -> RecipeEquipmentRequirementListResponse:
    try:
        requirements = service.list(recipe_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return RecipeEquipmentRequirementListResponse(
        items=[_response(item) for item in requirements]
    )


@router.post(
    "/{recipe_id}/equipment-requirements",
    response_model=RecipeEquipmentRequirementResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_requirement(
    recipe_id: str,
    request: RecipeEquipmentRequirementWriteRequest,
    service: RecipeEquipmentService = Depends(get_service),
) -> RecipeEquipmentRequirementResponse:
    try:
        requirement = service.add(recipe_id, **request.model_dump())
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(requirement)


@router.put(
    "/{recipe_id}/equipment-requirements/{requirement_id}",
    response_model=RecipeEquipmentRequirementResponse,
)
def update_requirement(
    recipe_id: str,
    requirement_id: str,
    request: RecipeEquipmentRequirementWriteRequest,
    service: RecipeEquipmentService = Depends(get_service),
) -> RecipeEquipmentRequirementResponse:
    try:
        requirement = service.update(
            recipe_id,
            requirement_id,
            **request.model_dump(),
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(requirement)


@router.delete(
    "/{recipe_id}/equipment-requirements/{requirement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_requirement(
    recipe_id: str,
    requirement_id: str,
    service: RecipeEquipmentService = Depends(get_service),
) -> Response:
    try:
        service.delete(recipe_id, requirement_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
