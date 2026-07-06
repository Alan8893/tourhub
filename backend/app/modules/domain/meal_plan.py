from dataclasses import dataclass
from typing import List


@dataclass
class MealPlan:
    """
    Generated meal plan for a trip.
    """

    id: str
    trip_id: str
    dish_ids: List[str]