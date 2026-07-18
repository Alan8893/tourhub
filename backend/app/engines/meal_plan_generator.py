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
    recipe_id: str | None = None


@dataclass(frozen=True)
class PreservedMealSlotInput:
    day_number: int
    meal_type: str
    dishes: list[DishInput]


@dataclass(frozen=True)
class MealPlanItemResult:
    day_number: int
    meal_type: str
    dish_id: str
    dish_name: str
    recipe_id: str | None = None


@dataclass(frozen=True)
class MealSlotResult:
    day_number: int
    meal_type: str
    dishes: list[DishInput]
    is_manually_edited: bool = False


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
        preserved_slots: Sequence[PreservedMealSlotInput] | None = None,
    ) -> MealPlanGenerationResult:
        if dishes_per_meal < 1:
            raise ValueError("dishes_per_meal must be greater than zero")

        meal_sequence = self._meal_sequence(days, meals_per_day, schedule)
        if role_aware:
            return self._generate_role_aware(dishes, meal_sequence, preserved_slots)
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

    @staticmethod
    def _preserved_slot_map(
        preserved_slots: Sequence[PreservedMealSlotInput] | None,
    ) -> dict[tuple[int, str], PreservedMealSlotInput]:
        result: dict[tuple[int, str], PreservedMealSlotInput] = {}
        for slot in preserved_slots or ():
            key = (slot.day_number, slot.meal_type)
            if key in result:
                raise ValueError("preserved meal slots must be unique by day and meal type")
            result[key] = slot
        return result

    def _generate_role_aware(
        self,
        dishes: list[DishInput],
        meal_sequence: list[tuple[int, str]],
        preserved_slots: Sequence[PreservedMealSlotInput] | None,
    ) -> MealPlanGenerationResult:
        warnings: list[str] = []
        warned_missing: set[tuple[str, str, str]] = set()
        items: list[MealPlanItemResult] = []
        slots: list[MealSlotResult] = []
        indexes: dict[tuple[str, str], int] = {}
        context = SelectionContext(used_for_day=set())
        preserved_by_key = self._preserved_slot_map(preserved_slots)

        for day_number, meal_type in meal_sequence:
            context.begin_day(day_number)
            preserved = preserved_by_key.get((day_number, meal_type))
            if preserved is not None:
                preserved_dishes = list(preserved.dishes)
                slots.append(
                    MealSlotResult(
                        day_number=day_number,
                        meal_type=meal_type,
                        dishes=preserved_dishes,
                        is_manually_edited=True,
                    )
                )
                items.extend(
                    MealPlanItemResult(
                        day_number,
                        meal_type,
                        dish.id,
                        dish.name,
                        dish.recipe_id,
                    )
                    for dish in preserved_dishes
                )
                continue

            composition = (
                (("snack", True),)
                if meal_type == "snack"
                else (
                    ("main", True),
                    ("addition", False),
                    ("drink", False),
                )
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
                context.register_selected(chosen, role, repeatable)

            slots.append(
                MealSlotResult(
                    day_number=day_number,
                    meal_type=meal_type,
                    dishes=selected,
                )
            )
            items.extend(
                MealPlanItemResult(
                    day_number,
                    meal_type,
                    dish.id,
                    dish.name,
                    dish.recipe_id,
                )
                for dish in selected
            )

        return MealPlanGenerationResult(items=items, slots=slots, warnings=warnings)

    @staticmethod
    def _candidates(
        dishes: list[DishInput],
        role: str,
        meal_type: str,
    ) -> list[DishInput]:
        return [
            dish
            for dish in dishes
            if any(
                assignment.role == role
                and meal_type in assignment.allowed_meal_types
                for assignment in dish.meal_roles
            )
        ]

    @staticmethod
    def _select_role_candidate(
        candidates: list[DishInput],
        start_index: int,
        context: SelectionContext,
        selected_ids: set[str],
        role: str,
        meal_type: str,
    ) -> tuple[DishInput | None, int, bool]:
        for offset in range(len(candidates)):
            index = (start_index + offset) % len(candidates)
            candidate = candidates[index]
            assignment = next(
                item
                for item in candidate.meal_roles
                if item.role == role and meal_type in item.allowed_meal_types
            )
            if candidate.id in selected_ids:
                continue
            if MealCompositionPolicy.can_select(
                candidate,
                context,
                assignment.is_repeatable,
                role,
            ):
                return candidate, (index + 1) % len(candidates), assignment.is_repeatable
        return None, start_index, False

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
        if reason == "catalogue":
            warnings.append(f"No {role} dishes available for {meal_type}")
        else:
            warnings.append(f"No eligible {role} dishes available for {meal_type}")

    @staticmethod
    def _generate_legacy(
        dishes: list[DishInput],
        meal_sequence: list[tuple[int, str]],
        dishes_per_meal: int,
    ) -> MealPlanGenerationResult:
        items: list[MealPlanItemResult] = []
        slots: list[MealSlotResult] = []
        for index, (day_number, meal_type) in enumerate(meal_sequence):
            selected = [
                dishes[(index * dishes_per_meal + offset) % len(dishes)]
                for offset in range(dishes_per_meal)
            ]
            slots.append(
                MealSlotResult(
                    day_number=day_number,
                    meal_type=meal_type,
                    dishes=selected,
                )
            )
            items.extend(
                MealPlanItemResult(
                    day_number,
                    meal_type,
                    dish.id,
                    dish.name,
                    dish.recipe_id,
                )
                for dish in selected
            )

        counts = Counter(item.dish_id for item in items)
        warnings = []
        if any(count > 1 for count in counts.values()):
            warnings.append(INSUFFICIENT_DISHES_WARNING)
        return MealPlanGenerationResult(items=items, slots=slots, warnings=warnings)
