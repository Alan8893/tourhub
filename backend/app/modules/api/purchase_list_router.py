from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.project_access import ProjectAccessPolicy
from app.core.session import get_session
from app.engines.documents.dto import GeneratedDocument
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator
from app.models.meal_plan import MealPlanORM
from app.models.purchase_list import PurchaseListORM
from app.models.user import UserORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.errors import ErrorResponse, ValidationErrorResponse
from app.schemas.purchase_list import (
    PurchaseListResponse,
    PurchaseListSummaryResponse,
    PurchaseListUpdate,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.operational_audit_service import OperationalAuditService
from app.services.purchase_list_service import PurchaseListService
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(
    prefix="/purchase-lists",
    tags=["Purchase Lists"],
)


def get_purchase_list_service(
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> PurchaseListService:
    return PurchaseListService(
        repository=PurchaseListRepository(session),
        meal_plan_repository=MealPlanRepository(session),
        shopping_service=MealPlanShoppingService(
            shopping_list_service=ShoppingListService(session)
        ),
        actor=actor,
    )


def _project_id_for_purchase_list(
    session: Session,
    purchase_list: PurchaseListORM,
) -> int:
    if purchase_list.project_id is not None:
        return purchase_list.project_id
    meal_plan = session.get(MealPlanORM, purchase_list.meal_plan_id)
    if meal_plan is None or meal_plan.project_id is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return meal_plan.project_id


def _record_document(
    *,
    service: PurchaseListService,
    purchase_list_id: str,
    document_format: str,
    document: GeneratedDocument,
) -> None:
    if service.actor is None:
        return
    session = service.repository.session
    OperationalAuditService(session).record_document_generated(
        actor=service.actor,
        source_entity_type="purchase_list",
        source_entity_id=purchase_list_id,
        document_kind="purchase_list",
        document_format=document_format,
        document=document,
    )
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise


@router.post("/from-meal-plan/{meal_plan_id}", response_model=PurchaseListResponse)
def create_purchase_list(
    meal_plan_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    meal_plan = session.get(MealPlanORM, meal_plan_id)
    if meal_plan is None or meal_plan.project_id is None:
        raise HTTPException(status_code=404, detail="Project not found")
    ProjectAccessPolicy.require_operational_write(session, meal_plan.project_id, actor)
    try:
        return service.create_from_meal_plan_id(meal_plan_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/project/{project_id}/generate", response_model=PurchaseListResponse)
def create_project_purchase_list(
    project_id: int,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    project = ProjectAccessPolicy.require_operational_write(session, project_id, actor)
    if not project.meal_plans:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    meal_plan = project.meal_plans[0]
    try:
        return service.create_from_meal_plan_id(
            str(meal_plan.id),
            project_id=project.id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/project/{project_id}", response_model=PurchaseListResponse)
def get_project_purchase_list(
    project_id: int,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    ProjectAccessPolicy.require_visible(session, project_id, actor)
    purchase_list = PurchaseListRepository(session).get_by_project_id(project_id)
    if not purchase_list:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    return purchase_list


@router.get("/{purchase_list_id}", response_model=PurchaseListResponse)
def get_purchase_list(
    purchase_list_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    purchase_list = service.get(purchase_list_id)
    if not purchase_list:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_purchase_list(session, purchase_list),
        actor,
    )
    return purchase_list


@router.patch(
    "/{purchase_list_id}",
    response_model=PurchaseListResponse,
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse},
    },
)
def update_purchase_list(
    purchase_list_id: str,
    payload: PurchaseListUpdate,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    purchase_list = service.get(purchase_list_id)
    if purchase_list is None:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    ProjectAccessPolicy.require_operational_write(
        session,
        _project_id_for_purchase_list(session, purchase_list),
        actor,
    )
    try:
        return service.update_responsible_person(
            purchase_list_id,
            payload.responsible_person,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{purchase_list_id}/summary", response_model=PurchaseListSummaryResponse)
def get_purchase_list_summary(
    purchase_list_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    purchase_list = service.get(purchase_list_id)
    if purchase_list is None:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_purchase_list(session, purchase_list),
        actor,
    )
    try:
        return service.get_summary(purchase_list_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{purchase_list_id}/export/pdf")
def export_purchase_list_pdf(
    purchase_list_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    purchase_list = service.get(purchase_list_id)
    if not purchase_list:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_purchase_list(session, purchase_list),
        actor,
    )
    document = service.create_document_dto(purchase_list)
    generated = PDFDocumentGenerator().generate(document)
    _record_document(
        service=service,
        purchase_list_id=purchase_list_id,
        document_format="pdf",
        document=generated,
    )
    return Response(
        content=generated.content,
        media_type=generated.content_type,
        headers={"Content-Disposition": f"attachment; filename={generated.filename}"},
    )


@router.get("/{purchase_list_id}/export/excel")
def export_purchase_list_excel(
    purchase_list_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
):
    purchase_list = service.get(purchase_list_id)
    if not purchase_list:
        raise HTTPException(status_code=404, detail="Purchase list not found")
    ProjectAccessPolicy.require_visible(
        session,
        _project_id_for_purchase_list(session, purchase_list),
        actor,
    )
    document = service.create_document_dto(purchase_list)
    generated = ExcelDocumentGenerator().generate(document)
    _record_document(
        service=service,
        purchase_list_id=purchase_list_id,
        document_format="excel",
        document=generated,
    )
    return Response(
        content=generated.content,
        media_type=generated.content_type,
        headers={"Content-Disposition": f"attachment; filename={generated.filename}"},
    )
