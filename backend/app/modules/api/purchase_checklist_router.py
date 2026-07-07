from fastapi import APIRouter

from app.schemas.purchase_checklist import PurchaseChecklistResponse


router = APIRouter(
    prefix="/purchase-checklists",
    tags=["Purchase Checklists"],
)


@router.get("/{checklist_id}", response_model=PurchaseChecklistResponse)
def get_purchase_checklist(checklist_id: str):
    """Get purchase checklist by id."""
    raise NotImplementedError
