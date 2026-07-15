from enum import StrEnum


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    SNACK = "snack"
    LUNCH = "lunch"
    DINNER = "dinner"


MEAL_TYPE_ORDER = tuple(MealType)
MEAL_TYPE_VALUES = tuple(meal_type.value for meal_type in MEAL_TYPE_ORDER)
MAIN_MEAL_TYPES = (
    MealType.BREAKFAST,
    MealType.LUNCH,
    MealType.DINNER,
)
