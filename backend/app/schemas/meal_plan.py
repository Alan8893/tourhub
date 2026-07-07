from pydantic import BaseModel, Field


class MealPlanGenerateRequest(BaseModel):
    """
    Request for automatic meal plan generation.
    """

    name: str = Field(
        min_length=1,
        max_length=255,
    )

    participants: int = Field(
        gt=0,
    )

    days: int = Field(
        gt=0,
    )

    meals_per_day: list[str] = Field(
        min_length=1,
    )


class MealPlanItemResponse(BaseModel):
    """
    Single generated meal.
    """

    day_number: int

    meal_type: str

    dish_id: str

    dish_name: str


class MealPlanResponse(BaseModel):
    """
    Generated meal plan response.
    """

    id: str

    name: str

    participants: int

    days_count: int

    items: list[MealPlanItemResponse]

    warnings: list[str] = []