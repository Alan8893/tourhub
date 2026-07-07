from fastapi import APIRouter

from app.schemas.meta import MetaResponse, WorkflowStatusesResponse
from app.domain.workflows.purchase_list import PurchaseListStatus
from app.domain.workflows.purchase_checklist import PurchaseChecklistStatus


router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("", response_model=MetaResponse)
async def get_meta() -> MetaResponse:
    return MetaResponse(
        name="TourHub",
        version="0.1.0",
        api_version="v1",
        statuses=WorkflowStatusesResponse(
            purchase_list=[status.value for status in PurchaseListStatus],
            purchase_checklist=[status.value for status in PurchaseChecklistStatus],
        ),
    )
