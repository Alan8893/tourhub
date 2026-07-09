from dataclasses import dataclass, field


@dataclass(frozen=True)
class DishInput:
    """Dish available for meal plan generation."""

    id: str
    name: str


@dataclass(frozen=True)
class MealPlanItemResult:
    """Generated dish assigned to a meal."""

    day_number: int
    meal_type: str
    dish_id: str
    dish_name: str


@dataclass(frozen=True)
class MealPlanGenerationResult:
    """Result of meal plan generation."""

    items: list[MealPlanItemResult]
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
        """
        Generate meal plan composition.

        Backward compatible:
        dishes_per_meal=1 keeps old behaviour.
        """

        if not dishes:
            return MealPlanGenerationResult(
                items=[],
                warnings=["No dishes available"],
            )

        if dishes_per_meal < 1:
            raise ValueError("dishes_per_meal must be greater than zero")

        if schedule is not None:
            meal_sequence = [
                (day.day_number, meal)
                for day in schedule
                for meal in day.meals
            ]
        else:
            meal_sequence = [
                (day_number, meal_type)
                for day_number in range(1, days + 1)
                for meal_type in (meals_per_day or [])
            ]

        warnings: list[str] = []
        result: list[MealPlanItemResult] = []

        required_dishes = len(meal_sequence) * dishes_per_meal

        if len(dishes) < required_dishes:
            warnings.append("Dish database is insufficient")

        dish_index = 0

        for day_number, meal_type in meal_sequence:
            used_for_meal: set[str] = set()

            for _ in range(dishes_per_meal):
                dish = dishes[dish_index % len(dishes)]

                attempts = 0
                while dish.id in used_for_meal and attempts < len(dishes):
                    dish_index += 1
                    dish = dishes[dish_index % len(dishes)]
                    attempts += 1

                result.append(
                    MealPlanItemResult(
                        day_number=day_number,
                        meal_type=meal_type,
                        dish_id=dish.id,
                        dish_name=dish.name,
                    )
                )

                used_for_meal.add(dish.id)
                dish_index += 1

        return MealPlanGenerationResult(
            items=result,
            warnings=warnings,
        )
