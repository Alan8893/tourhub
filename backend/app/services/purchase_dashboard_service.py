from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.purchase_dashboard import (
    PurchaseDashboardChecklistResponse,
    PurchaseDashboardDocumentResponse,
    PurchaseDashboardPurchaseListResponse,
    PurchaseDashboardResponse,
)


class PurchaseDashboardService:
    """Application service for purchase dashboard aggregation."""

    def __init__(
        self,
        purchase_list_repository: PurchaseListRepository,
        purchase_checklist_repository: PurchaseChecklistRepository,
    ):
        self.purchase_list_repository = purchase_list_repository
        self.purchase_checklist_repository = purchase_checklist_repository

    def get_dashboard(self, meal_plan_id: str) -> PurchaseDashboardResponse:
        purchase_list = self.purchase_list_repository.get_by_meal_plan_id(meal_plan_id)
        checklist = self.purchase_checklist_repository.get_by_meal_plan_id(meal_plan_id)

        purchase_list_response = PurchaseDashboardPurchaseListResponse(
            id=purchase_list.id if purchase_list else None,
            status=purchase_list.status if purchase_list else None,
            items_total=len(purchase_list.items) if purchase_list else 0,
            packages_total=sum(item.packages_count for item in purchase_list.items) if purchase_list else 0,
        )

        total_items = len(checklist.items) if checklist else 0
        checked_items = sum(1 for item in checklist.items if item.is_checked) if checklist else 0

        checklist_response = PurchaseDashboardChecklistResponse(
            id=checklist.id if checklist else None,
            status=checklist.status if checklist else None,
            total_items=total_items,
            checked_items=checked_items,
            progress_percent=round((checked_items / total_items) * 100, 2) if total_items else 0,
        )

        return PurchaseDashboardResponse(
            meal_plan_id=meal_plan_id,
            purchase_list=purchase_list_response,
            checklist=checklist_response,
            documents=PurchaseDashboardDocumentResponse(
                pdf_available=purchase_list is not None,
                excel_available=purchase_list is not None,
            ),
        )
