from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.workflows.purchase_checklist import PurchaseChecklistStatus


class PurchaseChecklistItemUpdate(BaseModel):
    is_checked: bool | None = None
    purchased_quantity: float | None = Field(default=None, ge=0)


class PurchaseChecklistItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    product_id: UUID
    product_name: str
    required_quantity: float
    purchased_quantity: float
    remaining_quantity: float
    unit: str
    is_checked: bool


class PurchaseChecklistResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: int | None
    meal_plan_id: UUID
    status: PurchaseChecklistStatus
    items: list[PurchaseChecklistItemResponse]


class PurchaseChecklistProgressResponse(BaseModel):
    id: UUID
    status: PurchaseChecklistStatus
    total_items: int
    checked_items: int
    progress_percent: float
