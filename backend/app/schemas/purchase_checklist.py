from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PurchaseChecklistItemUpdate(BaseModel):
    is_checked: bool | None = None
    purchased_quantity: float | None = None


class PurchaseChecklistItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    product_id: UUID
    required_quantity: float
    purchased_quantity: float
    unit: str
    is_checked: bool


class PurchaseChecklistResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    meal_plan_id: UUID
    status: str
    items: list[PurchaseChecklistItemResponse]


class PurchaseChecklistProgressResponse(BaseModel):
    id: UUID
    status: str
    total_items: int
    checked_items: int
    progress_percent: float
