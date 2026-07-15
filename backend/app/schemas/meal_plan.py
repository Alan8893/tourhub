from uuid import UUID

from pydantic import BaseModel, Field


class MealPlanItemResponse(BaseModel):
    """Single dish inside the legacy flat meal-plan view."""

    day_number: int
    meal_type: str
    dish_id: UUID
    dish_name: str


class MealSlotDishResponse(BaseModel):
    """Dish membership inside a persisted MealSlot."""

    id: str
    dish_id: UUID
    dish_name: str


class MealSlotResponse(BaseModel):
    """A meal slot containing one or more dishes."""

    id: str
    day_number: int
    meal_type: str
    dishes: list[MealSlotDishResponse]


class MealPlanResponse(BaseModel):
    """Persisted meal-plan response."""

    id: UUID
    project_id: int | None = None
    name: str
    participants: int
    days_count: int
    items: list[MealPlanItemResponse]
    meals: list[MealSlotResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
