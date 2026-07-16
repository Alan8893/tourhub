from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.modules.domain.meal_role import MealRole
from app.modules.domain.meal_type import MealType

if TYPE_CHECKING:
    from app.engines.meal_plan_generator import DishInput


REQUIRED_ROLE_BY_MEAL_TYPE: dict[MealType, MealRole] = {
    MealType.BREAKFAST: MealRole.MAIN,
    MealType.SNACK: MealRole.SNACK,
    MealType.LUNCH: MealRole.MAIN,
    MealType.DINNER: MealRole.MAIN,
}


@dataclass
class SelectionContext:
    """Selection state for persisted role-aware generation rules."""

    used_for_day: set[str]

    def reset_day(self) -> None:
        self.used_for_day.clear()

    def register_selected(self, dish: "DishInput") -> None:
        self.used_for_day.add(dish.id)


class MealCompositionPolicy:
    """Pure role and meal-type rules used by automatic generation."""

    @staticmethod
    def required_role(meal_type: str) -> MealRole:
        try:
            normalized_meal_type = MealType(meal_type)
        except ValueError as exc:
            raise ValueError(f"Unsupported meal type: {meal_type}") from exc
        return REQUIRED_ROLE_BY_MEAL_TYPE[normalized_meal_type]

    @staticmethod
    def can_select(
        dish: "DishInput",
        context: SelectionContext,
        meal_type: str,
        role: MealRole,
    ) -> bool:
        assignment = dish.assignment_for(role=role, meal_type=meal_type)
        if assignment is None:
            return False
        return assignment.is_repeatable or dish.id not in context.used_for_day
