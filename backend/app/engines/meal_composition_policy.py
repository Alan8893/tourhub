from dataclasses import dataclass

from app.engines.meal_plan_generator import DishInput


@dataclass
class SelectionContext:
    """State used by menu composition rules during generation."""

    used_for_day: set[str]
    recent_main_ids: set[str]


class MealCompositionPolicy:
    """Pure rules for selecting dishes without persistence dependencies."""

    @staticmethod
    def can_select(dish: DishInput, context: SelectionContext) -> bool:
        if dish.id in context.used_for_day:
            return False

        if dish.is_main and dish.id in context.recent_main_ids:
            return False

        return True
