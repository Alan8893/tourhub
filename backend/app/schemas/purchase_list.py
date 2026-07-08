from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.workflows.purchase_list import PurchaseListStatus


class PurchaseListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    product_id: UUID
    required_quantity: float
    required_unit: str
    package_size: float
    package_unit: str
    packages_count: int


class PurchaseListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: int | None
    meal_plan_id: UUID
    status: PurchaseListStatus
    items: list[PurchaseListItemResponse]


class PurchaseListSummaryResponse(BaseModel):
    id: UUID
    status: PurchaseListStatus
    items_total: int
    packages_total: int
