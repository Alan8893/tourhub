from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from app.engines.meal_composition_policy import MealCompositionPolicy, SelectionContext


class MealScheduleDayInput(Protocol):
    day_number: int
    meals: list[str]


INSUFFICIENT_DISHES_WARNING = "Dish database is insufficient"


@dataclass(frozen=True)
class DishRoleInput:
    role: str
    allowed_meal_types: tuple[str, ...]
    is_repeatable: bool = False


@dataclass(frozen=True)
class DishInput:
    id: str
    name: str
    meal_roles: tuple[DishRoleInput, ...] = ()


@dataclass(frozen=True)
class MealPlanItemResult:
    day_number: int
    meal_type: str
    dish_id: str
    dish_name: str


@dataclass(frozen=True)
class MealSlotResult:
    day_number: int
    meal_type: str
    dishes: list[DishInput]


@dataclass(frozen=True)
class MealPlanGenerationResult:
    items: list[MealPlanItemResult]
    slots: list[MealSlotResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class MealPlanGenerator:
    def generate(
        self,
        dishes: list[DishInput],
        days: int,
        meals_per_day: list[str] | None = None,
        schedule: Sequence[MealScheduleDayInput] | None = None,
        dishes_per_meal: int = 1,
        role_aware: bool = False,
    ) -> MealPlanGenerationResult:
        if dishes_per_meal < 1:
            raise ValueError("dishes_per_meal must be greater than zero")

        meal_sequence = self._meal_sequence(days, meals_per_day, schedule)
        if role_aware:
            return self._generate_role_aware(dishes, meal_sequence)
        if not dishes:
            return MealPlanGenerationResult(items=[], slots=[], warnings=["No dishes available"])
        return self._generate_legacy(dishes, meal_sequence, dishes_per_meal)

    @staticmethod
    def _meal_sequence(
        days: int,
        meals_per_day: list[str] | None,
        schedule: Sequence[MealScheduleDayInput] | None,
    ) -> list[tuple[int, str]]:
        if schedule is not None:
            return [(day.day_number, meal) for day in schedule for meal in day.meals]
        return [
            (day_number, meal_type)
            for day_number in range(1, days + 1)
            for meal_type in (meals_per_day or [])
        ]

    def _generate_role_aware(
        self,
        dishes: list[DishInput],
        meal_sequence: list[tuple[int, str]],
    ) -> MealPlanGenerationResult:
        warnings: list[str] = []
        warned_missing: set[tuple[str, str, str]] = set()
        items: list[MealPlanItemResult] = []
        slots: list[MealSlotResult] = []
        indexes: dict[tuple[str, str], int] = {}
        context = SelectionContext(used_for_day=set())

        for day_number, meal_type in meal_sequence:
            context.begin_day(day_number)

            composition = (("snack", True),) if meal_type == "snack" else (
                ("main", True),
                ("addition", False),
                ("drink", False),
            )
            selected: list[DishInput] = []
            selected_ids: set[str] = set()

            for role, required in composition:
                candidates = self._candidates(dishes, role, meal_type)
                if not candidates:
                    self._warn_required_gap(
                        warnings,
                        warned_missing,
                        meal_type,
                        role,
                        required,
                        reason="catalogue",
                    )
                    continue

                index_key = (meal_type, role)
                chosen, next_index, repeatable = self._select_role_candidate(
                    candidates,
                    indexes.get(index_key, 0),
                    context,
                    selected_ids,
                    role,
                    meal_type,
                )
                indexes[index_key] = next_index
                if chosen is None:
                    self._warn_required_gap(
                        warnings,
                        warned_missing,
                        meal_type,
                        role,
                        required,
                        reason="eligible",
                    )
                    continue
                selected.append(chosen)
                selected_ids.add(chosen.id)
                context.register_selected(
                    chosen,
                    role=role,
                    is_repeatable=repeatable,
                )
                items.append(MealPlanItemResult(day_number, meal_type, chosen.id, chosen.name))

            slots.append(MealSlotResult(day_number, meal_type, selected))

        return MealPlanGenerationResult(items=items, slots=slots, warnings=warnings)

    @staticmethod
    def _warn_required_gap(
        warnings: list[str],
        warned_missing: set[tuple[str, str, str]],
        meal_type: str,
        role: str,
        required: bool,
        reason: str,
    ) -> None:
        if not required:
            return
        key = (meal_type, role, reason)
        if key in warned_missing:
            return
        warned_missing.add(key)
        if reason == "eligible":
            warnings.append(f"No eligible {role} dishes available for {meal_type}")
        else:
            warnings.append(f"No {role} dishes available for {meal_type}")

    @staticmethod
    def _candidates(dishes: list[DishInput], role: str, meal_type: str) -> list[DishInput]:
        return [
            dish
            for dish in dishes
            if any(
                assignment.role == role and meal_type in assignment.allowed_meal_types
                for assignment in dish.meal_roles
            )
        ]

    @staticmethod
    def _assignment(dish: DishInput, role: str, meal_type: str) -> DishRoleInput:
        return next(
            assignment
            for assignment in dish.meal_roles
            if assignment.role == role and meal_type in assignment.allowed_meal_types
        )

    def _select_role_candidate(
        self,
        candidates: list[DishInput],
        start_index: int,
        context: SelectionContext,
        selected_ids: set[str],
        role: str,
        meal_type: str,
    ) -> tuple[DishInput | None, int, bool]:
        for offset in range(len(candidates)):
            candidate_index = start_index + offset
            candidate = candidates[candidate_index % len(candidates)]
            assignment = self._assignment(candidate, role, meal_type)
            if candidate.id in selected_ids:
                continue
            if not MealCompositionPolicy.can_select(
                candidate,
                context,
                assignment.is_repeatable,
                role,
            ):
                continue
            return candidate, candidate_index + 1, assignment.is_repeatable

        return None, start_index + 1, False

    def _generate_legacy(
        self,
        dishes: list[DishInput],
        meal_sequence: list[tuple[int, str]],
        dishes_per_meal: int,
    ) -> MealPlanGenerationResult:
        warnings: list[str] = []
        items: list[MealPlanItemResult] = []
        slots: list[MealSlotResult] = []
        meals_by_day = Counter(day_number for day_number, _ in meal_sequence)
        if len(dishes) < max(meals_by_day.values(), default=0) * dishes_per_meal:
            warnings.append(INSUFFICIENT_DISHES_WARNING)

        dish_index = 0
        context = SelectionContext(used_for_day=set())
        for day_number, meal_type in meal_sequence:
            context.begin_day(day_number)
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
