from collections import Counter
from dataclasses import dataclass, field

from app.engines.meal_composition_policy import MealCompositionPolicy, SelectionContext


INSUFFICIENT_DISHES_WARNING = "Dish database is insufficient"


@dataclass(frozen=True)
class DishInput:
    """Dish available for meal plan generation."""

    id: str
    name: str
    is_main: bool = True


@dataclass(frozen=True)
class MealPlanItemResult:
    """Legacy generated dish assigned to a meal."""

    day_number: int
    meal_type: str
    dish_id: str
    dish_name: str


@dataclass(frozen=True)
class MealSlotResult:
    """Generated meal slot with one or more dishes."""

    day_number: int
    meal_type: str
    dishes: list[DishInput]


@dataclass(frozen=True)
class MealPlanGenerationResult:
    """Result of meal plan generation."""

    items: list[MealPlanItemResult]
    slots: list[MealSlotResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class MealPlanGenerator:
    """
    Pure meal plan generation engine.

    No database.
    No ORM.
    No API.
    """

    def generate(
        self,
        dishes: list[DishInput],
        days: int,
        meals_per_day: list[str] | None = None,
        schedule: list[object] | None = None,
        dishes_per_meal: int = 1,
    ) -> MealPlanGenerationResult:
        if not dishes:
            return MealPlanGenerationResult(items=[], slots=[], warnings=["No dishes available"])
        if dishes_per_meal < 1:
            raise ValueError("dishes_per_meal must be greater than zero")

        if schedule is not None:
            meal_sequence = [(day.day_number, meal) for day in schedule for meal in day.meals]
        else:
            meal_sequence = [
                (day_number, meal_type)
                for day_number in range(1, days + 1)
                for meal_type in (meals_per_day or [])
            ]

        warnings: list[str] = []
        items: list[MealPlanItemResult] = []
        slots: list[MealSlotResult] = []

        meals_by_day = Counter(day_number for day_number, _ in meal_sequence)
        if len(dishes) < max(meals_by_day.values(), default=0) * dishes_per_meal:
            warnings.append(INSUFFICIENT_DISHES_WARNING)

        dish_index = 0
        current_day: int | None = None
        context = SelectionContext(used_for_day=set())

        for day_number, meal_type in meal_sequence:
            if day_number != current_day:
                current_day = day_number
                context.used_for_day = set()

            selected: list[DishInput] = []
            for _ in range(dishes_per_meal):
                dish, dish_index = self._select_next_dish(dishes, dish_index, context)
                selected.append(dish)
                context.register_selected(dish)
                items.append(MealPlanItemResult(day_number, meal_type, dish.id, dish.name))

            slots.append(MealSlotResult(day_number, meal_type, selected))

        return MealPlanGenerationResult(items=items, slots=slots, warnings=warnings)

    @staticmethod
    def _select_next_dish(
        dishes: list[DishInput],
        start_index: int,
        context: SelectionContext,
    ) -> tuple[DishInput, int]:
        for offset in range(len(dishes)):
            candidate_index = start_index + offset
            candidate = dishes[candidate_index % len(dishes)]
            if not MealCompositionPolicy.can_select(candidate, context):
                continue
            return candidate, candidate_index + 1

        fallback = dishes[start_index % len(dishes)]
        return fallback, start_index + 1
