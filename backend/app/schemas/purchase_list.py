from pydantic import BaseModel, ConfigDict


class PurchaseListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    product_id: str
    required_quantity: float
    required_unit: str
    package_size: float
    package_unit: str
    packages_count: int


class PurchaseListResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: str
    meal_plan_id: str
    status: str
    items: list[PurchaseListItemResponse]
