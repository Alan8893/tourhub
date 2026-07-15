from enum import StrEnum


class MealRole(StrEnum):
    MAIN = "main"
    ADDITION = "addition"
    DRINK = "drink"
    SNACK = "snack"


MEAL_ROLE_ORDER = tuple(MealRole)
MEAL_ROLE_VALUES = tuple(role.value for role in MEAL_ROLE_ORDER)
