from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.purchase_list import PurchaseListResponse
from app.services.purchase_list_service import PurchaseListService


router = APIRouter(
    prefix="/purchase-lists",
    tags=["Purchase Lists"],
)


def get_purchase_list_service(
    session: Session = Depends(get_session),
) -> PurchaseListService:
    return PurchaseListService(
        repository=PurchaseListRepository(session),
    )


@router.get(
    "/{purchase_list_id}",
    response_model=PurchaseListResponse,
)
def get_purchase_list(
    purchase_list_id: str,
    service: PurchaseListService = Depends(get_purchase_list_service),
):
    purchase_list = service.get(purchase_list_id)

    if not purchase_list:
        raise HTTPException(
            status_code=404,
            detail="Purchase list not found",
        )

    return purchase_list
