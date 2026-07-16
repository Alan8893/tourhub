from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from app.engines.meal_composition_policy import MealCompositionPolicy, SelectionContext
from app.modules.domain.meal_role import MealRole


class MealScheduleDayInput(Protocol):
    day_number: int
    meals: list[str]


INSUFFICIENT_DISHES_WARNING = "Dish database is insufficient"
NO_DISHES_WARNING = "No dishes available"


def missing_required_role_warning(role: MealRole, meal_type: str) -> str:
    return f"No compatible {role.value} dishes available for {meal_type}"


@dataclass(frozen=True)
class DishRoleInput:
    """Persisted role assignment available to the pure generator."""

    role: str
    allowed_meal_types: frozenset[str]
    is_repeatable: bool = False


@dataclass(frozen=True)
class DishInput:
    """Dish available for role-aware meal plan generation."""

    id: str
    name: str
    meal_roles: tuple[DishRoleInput, ...] = ()

    def assignment_for(self, role: MealRole, meal_type: str) -> DishRoleInput | None:
        for assignment in self.meal_roles:
            if assignment.role == role.value and meal_type in assignment.allowed_meal_types:
                return assignment
        return None


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
        schedule: Sequence[MealScheduleDayInput] | None = None,
        dishes_per_meal: int = 1,
    ) -> MealPlanGenerationResult:
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
        if not dishes:
            self._append_warning(warnings, NO_DISHES_WARNING)

        pool_indices: dict[tuple[str, str], int] = {}
        current_day: int | None = None
        context = SelectionContext(used_for_day=set())

        for day_number, meal_type in meal_sequence:
            if day_number != current_day:
                current_day = day_number
                context.reset_day()

            required_role = MealCompositionPolicy.required_role(meal_type)
            compatible_dishes = [
                dish
                for dish in dishes
                if dish.assignment_for(required_role, meal_type) is not None
            ]
            if not compatible_dishes:
                self._append_warning(
                    warnings,
                    missing_required_role_warning(required_role, meal_type),
                )
                slots.append(MealSlotResult(day_number, meal_type, []))
                continue

            pool_key = (required_role.value, meal_type)
            dish_index = pool_indices.get(pool_key, 0)
            selected: list[DishInput] = []
            for _ in range(dishes_per_meal):
                dish, dish_index, exhausted = self._select_next_dish(
                    compatible_dishes,
                    dish_index,
                    context,
                    meal_type,
                    required_role,
                )
                if exhausted:
                    self._append_warning(warnings, INSUFFICIENT_DISHES_WARNING)
                selected.append(dish)
                context.register_selected(dish)
                items.append(MealPlanItemResult(day_number, meal_type, dish.id, dish.name))

            pool_indices[pool_key] = dish_index
            slots.append(MealSlotResult(day_number, meal_type, selected))

        return MealPlanGenerationResult(items=items, slots=slots, warnings=warnings)

    @staticmethod
    def _select_next_dish(
        dishes: list[DishInput],
        start_index: int,
        context: SelectionContext,
        meal_type: str,
        role: MealRole,
    ) -> tuple[DishInput, int, bool]:
        for offset in range(len(dishes)):
            candidate_index = start_index + offset
            candidate = dishes[candidate_index % len(dishes)]
            if not MealCompositionPolicy.can_select(
                candidate,
                context,
                meal_type,
                role,
            ):
                continue
            return candidate, candidate_index + 1, False

        fallback = dishes[start_index % len(dishes)]
        return fallback, start_index + 1, True

    @staticmethod
    def _append_warning(warnings: list[str], warning: str) -> None:
        if warning not in warnings:
            warnings.append(warning)
