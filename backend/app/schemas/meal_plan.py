from pydantic import BaseModel, Field
from uuid import UUID


class MealPlanGenerateRequest(BaseModel):
    """Request for automatic meal plan generation."""

    name: str = Field(min_length=1, max_length=255)
    participants: int = Field(gt=0)
    days: int = Field(gt=0)
    meals_per_day: list[str] = Field(min_length=1)


class MealPlanItemResponse(BaseModel):
    """Single generated meal."""

    day_number: int
    meal_type: str
    dish_id: UUID
    dish_name: str


class MealPlanResponse(BaseModel):
    """Generated meal plan response."""

    id: UUID
    name: str
    participants: int
    days_count: int
    items: list[MealPlanItemResponse]
    warnings: list[str] = []


class ShoppingListItemResponse(BaseModel):
    product_name: str
    amount: float
    unit: str


class ShoppingListResponse(BaseModel):
    items: list[ShoppingListItemResponse]


class PackagedShoppingItemResponse(BaseModel):
    product_name: str
    amount: float
    unit: str
    package_size: float
    packages: int


class PackagedShoppingResponse(BaseModel):
    items: list[PackagedShoppingItemResponse]


class MealPlanGenerateResponse(BaseModel):
    meal_plan: MealPlanResponse
    shopping_list: ShoppingListResponse
    purchase_list: PackagedShoppingResponse
