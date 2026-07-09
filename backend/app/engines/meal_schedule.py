from dataclasses import dataclass


MEAL_ORDER = [
    "breakfast",
    "lunch",
    "dinner",
]


@dataclass(frozen=True)
class MealScheduleDay:
    day_number: int
    meals: list[str]


class MealScheduleEngine:
    """
    Pure engine responsible for building meal schedule.

    No database.
    No ORM.
    No API.
    """

    def build(
        self,
        days: int,
        start_meal: str,
        end_meal: str,
    ) -> list[MealScheduleDay]:
        if days < 1:
            raise ValueError("days must be greater than zero")

        if start_meal not in MEAL_ORDER:
            raise ValueError("invalid start meal")

        if end_meal not in MEAL_ORDER:
            raise ValueError("invalid end meal")

        if days == 1:
            start_index = MEAL_ORDER.index(start_meal)
            end_index = MEAL_ORDER.index(end_meal)

            if start_index > end_index:
                raise ValueError(
                    "single day schedule cannot finish before it starts"
                )

            return [
                MealScheduleDay(
                    day_number=1,
                    meals=MEAL_ORDER[start_index:end_index + 1],
                )
            ]

        result: list[MealScheduleDay] = []

        start_index = MEAL_ORDER.index(start_meal)
        end_index = MEAL_ORDER.index(end_meal)

        result.append(
            MealScheduleDay(
                day_number=1,
                meals=MEAL_ORDER[start_index:],
            )
        )

        for day_number in range(2, days):
            result.append(
                MealScheduleDay(
                    day_number=day_number,
                    meals=MEAL_ORDER.copy(),
                )
            )

        result.append(
            MealScheduleDay(
                day_number=days,
                meals=MEAL_ORDER[:end_index + 1],
            )
        )

        return result
