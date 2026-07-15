from enum import StrEnum


class MealDishRole(StrEnum):
    """Role of a dish inside generated menu composition."""

    MAIN = "main"
    SNACK = "snack"
