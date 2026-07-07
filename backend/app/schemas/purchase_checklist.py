from pydantic import BaseModel, ConfigDict


class PurchaseChecklistItemUpdate(BaseModel):
    is_checked: bool | None = None
    purchased_quantity: float | None = None


class PurchaseChecklistItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    product_id: str
    required_quantity: float
    purchased_quantity: float
    unit: str
    is_checked: bool


class PurchaseChecklistResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    meal_plan_id: str
    status: str
    items: list[PurchaseChecklistItemResponse]


class PurchaseChecklistProgressResponse(BaseModel):
    id: str
    status: str
    total_items: int
    checked_items: int
    progress_percent: float
