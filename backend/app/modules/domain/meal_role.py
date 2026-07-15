from enum import StrEnum

from app.modules.domain.meal_type import MAIN_MEAL_TYPES, MealType


class MealRole(StrEnum):
    MAIN = "main"
    ADDITION = "addition"
    DRINK = "drink"
    SNACK = "snack"


MEAL_ROLE_ORDER = tuple(MealRole)
MEAL_ROLE_VALUES = tuple(role.value for role in MEAL_ROLE_ORDER)
MEAL_ROLE_ALLOWED_MEAL_TYPES: dict[MealRole, frozenset[MealType]] = {
    MealRole.MAIN: frozenset(MAIN_MEAL_TYPES),
    MealRole.ADDITION: frozenset(MAIN_MEAL_TYPES),
    MealRole.DRINK: frozenset(MAIN_MEAL_TYPES),
    MealRole.SNACK: frozenset((MealType.SNACK,)),
}
