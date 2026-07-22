from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.project_access import ProjectAccessPolicy
from app.core.session import get_session
from app.models.meal_plan import MealPlanORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.user import UserORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.schemas.errors import ErrorResponse, ValidationErrorResponse
from app.schemas.purchase_checklist import (
    PurchaseChecklistItemResponse,
    PurchaseChecklistItemUpdate,
    PurchaseChecklistProgressResponse,
    PurchaseChecklistResponse,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.purchase_checklist_service import (
    PurchaseChecklistProgress,
    PurchaseChecklistService,
)
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/purchase-checklists", tags=["Purchase Checklists"])


def get_purchase_checklist_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistService:
    return PurchaseChecklistService(
        repository=PurchaseChecklistRepository(session),
        meal_plan_repository=MealPlanRepository(session),
        shopping_service=MealPlanShoppingService(
            shopping_list_service=ShoppingListService(session)
        ),
        actor=actor,
    )


def _project_id_for_checklist(
    session: Session,
    checklist: PurchaseChecklistORM,
) -> int:
    if checklist.project_id is not None:
        return checklist.project_id
    meal_plan = session.get(MealPlanORM, checklist.meal_plan_id)
    if meal_plan is None or meal_plan.project_id is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return meal_plan.project_id


@router.post(
    "/from-meal-plan/{meal_plan_id}",
    response_model=PurchaseChecklistResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def create_purchase_checklist(
    meal_plan_id: str,
    service: PurchaseChecklistService = Depends(get_purchase_checklist_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistORM:
    meal_plan = session.get(MealPlanORM, meal_plan_id)
    if meal_plan is None or meal_plan.project_id is None:
        raise HTTPException(status_code=404, detail="Project not found")
    ProjectAccessPolicy.require_operational_write(session, meal_plan.project_id, actor)
    try:
        return service.create_from_meal_plan_id(meal_plan_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/project/{project_id}/generate", response_model=PurchaseChecklistResponse)
def create_project_purchase_checklist(
    project_id: int,
    service: PurchaseChecklistService = Depends(get_purchase_checklist_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistORM:
    project = ProjectAccessPolicy.require_operational_write(session, project_id, actor)
    if not project.meal_plans:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    try:
        return service.create_from_meal_plan_id(
            str(project.meal_plans[0].id),
            project_id=project.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/project/{project_id}", response_model=PurchaseChecklistResponse)
def get_project_purchase_checklist(
    project_id: int,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistORM:
    ProjectAccessPolicy.require_visible(session, project_id, actor)
    checklist = PurchaseChecklistRepository(session).get_by_project_id(project_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Purchase checklist not found")
    return checklist


@router.get(
    "/{checklist_id}",
    response_model=PurchaseChecklistResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_purchase_checklist(
    checklist_id: str,
    service: PurchaseChecklistService = Depends(get_purchase_checklist_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistORM:
    checklist = service.get(checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Purchase checklist not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_checklist(session, checklist),
        actor,
    )
    return checklist


@router.get(
    "/{checklist_id}/progress",
    response_model=PurchaseChecklistProgressResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_purchase_checklist_progress(
    checklist_id: str,
    service: PurchaseChecklistService = Depends(get_purchase_checklist_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistProgress:
    checklist = service.get(checklist_id)
    if checklist is None:
        raise HTTPException(status_code=404, detail="Purchase checklist not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_checklist(session, checklist),
        actor,
    )
    try:
        return service.get_progress(checklist_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch(
    "/items/{item_id}",
    response_model=PurchaseChecklistItemResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def update_purchase_checklist_item(
    item_id: str,
    payload: PurchaseChecklistItemUpdate,
    service: PurchaseChecklistService = Depends(get_purchase_checklist_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseChecklistItemORM:
    item = session.get(PurchaseChecklistItemORM, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Purchase checklist item not found")
    checklist = session.get(PurchaseChecklistORM, item.checklist_id)
    if checklist is None:
        raise HTTPException(status_code=404, detail="Purchase checklist not found")
    ProjectAccessPolicy.require_operational_write(
        session,
        _project_id_for_checklist(session, checklist),
        actor,
    )
    try:
        return service.update_item(
            item_id=item_id,
            checked=payload.is_checked,
            purchased_quantity=payload.purchased_quantity,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
