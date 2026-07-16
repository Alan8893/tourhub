import typing
from dataclasses import dataclass, field


MAIN_DIVERSITY_DAYS = 3


class DishSelectionInput(typing.Protocol):
    @property
    def id(self) -> str:
        ...


@dataclass
class SelectionContext:
    used_for_day: set[str]
    current_day: int | None = None
    main_last_selected_day: dict[str, int] = field(default_factory=dict)

    def begin_day(self, day_number: int) -> None:
        if self.current_day is not None and day_number < self.current_day:
            raise ValueError("day_number must not move backwards")
        if day_number == self.current_day:
            return
        self.current_day = day_number
        self.reset_day()

    def reset_day(self) -> None:
        self.used_for_day.clear()

    def register_selected(
        self,
        dish: DishSelectionInput,
        role: str | None = None,
        is_repeatable: bool = False,
    ) -> None:
        if is_repeatable:
            return
        self.used_for_day.add(dish.id)
        if role != "main":
            return
        if self.current_day is None:
            raise ValueError("current day is required for main-dish diversity")
        self.main_last_selected_day[dish.id] = self.current_day

    def main_used_within_diversity_window(self, dish_id: str) -> bool:
        if self.current_day is None:
            return False
        previous_day = self.main_last_selected_day.get(dish_id)
        if previous_day is None:
            return False
        return self.current_day - previous_day < MAIN_DIVERSITY_DAYS


class MealCompositionPolicy:
    @staticmethod
    def can_select(
        dish: DishSelectionInput,
        context: SelectionContext,
        is_repeatable: bool = False,
        role: str | None = None,
    ) -> bool:
        if is_repeatable:
            return True
        if dish.id in context.used_for_day:
            return False
        return role != "main" or not context.main_used_within_diversity_window(dish.id)
