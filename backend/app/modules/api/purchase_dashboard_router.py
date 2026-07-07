from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.purchase_dashboard import PurchaseDashboardResponse
from app.services.purchase_dashboard_service import PurchaseDashboardService


router = APIRouter(
    prefix="/meal-plans",
    tags=["Purchase Dashboard"],
)


def get_purchase_dashboard_service(
    session: Session = Depends(get_session),
) -> PurchaseDashboardService:
    return PurchaseDashboardService(
        purchase_list_repository=PurchaseListRepository(session),
        purchase_checklist_repository=PurchaseChecklistRepository(session),
    )


@router.get(
    "/{meal_plan_id}/purchase-dashboard",
    response_model=PurchaseDashboardResponse,
)
def get_purchase_dashboard(
    meal_plan_id: str,
    service: PurchaseDashboardService = Depends(get_purchase_dashboard_service),
):
    return service.get_dashboard(meal_plan_id)
