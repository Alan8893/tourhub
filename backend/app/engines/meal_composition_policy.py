from dataclasses import dataclass
from typing import Protocol


class DishSelectionInput(Protocol):
    id: str


@dataclass
class SelectionContext:
    used_for_day: set[str]

    def reset_day(self) -> None:
        self.used_for_day.clear()

    def register_selected(
        self,
        dish: DishSelectionInput,
        is_repeatable: bool = False,
    ) -> None:
        if not is_repeatable:
            self.used_for_day.add(dish.id)


class MealCompositionPolicy:
    @staticmethod
    def can_select(
        dish: DishSelectionInput,
        context: SelectionContext,
        is_repeatable: bool = False,
    ) -> bool:
        return is_repeatable or dish.id not in context.used_for_day
