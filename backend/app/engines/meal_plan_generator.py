from dataclasses import dataclass, field


@dataclass(frozen=True)
class DishInput:
    """
    Dish available for meal plan generation.
    """

    id: str
    name: str


@dataclass(frozen=True)
class MealPlanItemResult:
    """
    Generated meal item.
    """

    day_number: int
    meal_type: str
    dish_id: str
    dish_name: str


@dataclass(frozen=True)
class MealPlanGenerationResult:
    """
    Result of meal plan generation.
    """

    items: list[MealPlanItemResult]

    warnings: list[str] = field(
        default_factory=list
    )


class MealPlanGenerator:
    """
    Pure meal plan generation engine.

    No database.
    No ORM.
    No API.

    Responsible only for menu generation.
    """

    def generate(
        self,
        dishes: list[DishInput],
        days: int,
        meals_per_day: list[str],
    ) -> MealPlanGenerationResult:
        """
        Generate meal plan.

        Rules:

        - deterministic result;
        - avoid consecutive dish repetition;
        - continue generation if dishes are insufficient;
        """

        if not dishes:
            return MealPlanGenerationResult(
                items=[],
                warnings=[
                    "No dishes available",
                ],
            )

        required_items = days * len(meals_per_day)

        warnings: list[str] = []

        if len(dishes) < required_items:
            warnings.append(
                "Dish database is insufficient"
            )

        result: list[MealPlanItemResult] = []

        previous_dish_id: str | None = None

        dish_index = 0

        for day_number in range(1, days + 1):
            for meal_type in meals_per_day:

                dish = dishes[dish_index % len(dishes)]

                if (
                    previous_dish_id == dish.id
                    and len(dishes) > 1
                ):
                    dish_index += 1
                    dish = dishes[dish_index % len(dishes)]

                result.append(
                    MealPlanItemResult(
                        day_number=day_number,
                        meal_type=meal_type,
                        dish_id=dish.id,
                        dish_name=dish.name,
                    )
                )

                previous_dish_id = dish.id
                dish_index += 1

        return MealPlanGenerationResult(
            items=result,
            warnings=warnings,
        )