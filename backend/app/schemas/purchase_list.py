from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.workflows.purchase_list import PurchaseListStatus


class PurchaseListUpdate(BaseModel):
    responsible_person: str | None = Field(default=None, max_length=255)


class PurchaseListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    product_id: UUID
    product_name: str
    required_quantity: float
    required_unit: str
    package_size: float
    package_unit: str
    packages_count: int
    purchase_quantity: float
    surplus_quantity: float


class PurchaseListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: int | None
    meal_plan_id: UUID
    status: PurchaseListStatus
    responsible_person: str | None
    items: list[PurchaseListItemResponse]


class PurchaseListSummaryResponse(BaseModel):
    id: UUID
    status: PurchaseListStatus
    items_total: int
    packages_total: int
