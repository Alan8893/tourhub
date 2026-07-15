from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.engines.meal_role import MealDishRole

if TYPE_CHECKING:
    from app.engines.meal_plan_generator import DishInput


@dataclass
class SelectionContext:
    """State used by menu composition rules during generation."""

    used_for_day: set[str]
    recent_main_ids: set[str] = field(default_factory=set)
    _recent_main_order: deque[str] = field(default_factory=lambda: deque(maxlen=3))

    def register_selected(self, dish: "DishInput") -> None:
        self.used_for_day.add(dish.id)
        if dish.role != MealDishRole.MAIN:
            return
        self._recent_main_order.append(dish.id)
        self.recent_main_ids = set(self._recent_main_order)


class MealCompositionPolicy:
    """Pure rules for selecting dishes without persistence dependencies."""

    @staticmethod
    def can_select(dish: "DishInput", context: SelectionContext) -> bool:
        if dish.id in context.used_for_day:
            return False

        if dish.role == MealDishRole.MAIN and dish.id in context.recent_main_ids:
            return False

        return True
