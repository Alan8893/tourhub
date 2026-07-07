from pydantic import BaseModel


class PurchaseChecklistItemUpdate(BaseModel):
    is_checked: bool | None = None
    purchased_quantity: float | None = None


class PurchaseChecklistItemResponse(BaseModel):
    id: str
    product_id: str
    required_quantity: float
    purchased_quantity: float
    unit: str
    is_checked: bool

    class Config:
        from_attributes = True


class PurchaseChecklistResponse(BaseModel):
    id: str
    meal_plan_id: str
    status: str
    items: list[PurchaseChecklistItemResponse]

    class Config:
        from_attributes = True
