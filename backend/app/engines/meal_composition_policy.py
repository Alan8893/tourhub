from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engines.meal_plan_generator import DishInput


@dataclass
class SelectionContext:
    """Selection state for rules supported by the current persisted dish model."""

    used_for_day: set[str]

    def reset_day(self) -> None:
        self.used_for_day.clear()

    def register_selected(self, dish: "DishInput") -> None:
        self.used_for_day.add(dish.id)


class MealCompositionPolicy:
    """Pure rules that are valid without persisted meal-role metadata."""

    @staticmethod
    def can_select(dish: "DishInput", context: SelectionContext) -> bool:
        return dish.id not in context.used_for_day
