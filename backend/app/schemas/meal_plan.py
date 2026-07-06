from pydantic import BaseModel
from typing import List, Dict


class MealPlanRequest(BaseModel):
    """
    Request DTO for meal plan generation.
    """

    dish_ids: List[str]
    days: int
    participants: int


class MealPlanResponse(BaseModel):
    """
    Response DTO for meal plan generation.
    """

    days: int
    participants: int
    dishes: List[str]
    shopping_list: Dict[str, float]