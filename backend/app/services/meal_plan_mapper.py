from app.models.meal_plan import MealPlanORM
from app.schemas.meal_plan import (
    MealPlanItemResponse,
    MealPlanResponse,
    MealSlotDishResponse,
    MealSlotResponse,
)


class MealPlanMapper:
    """Maps MealPlan ORM entities to API schemas."""

    @staticmethod
    def to_response(
        meal_plan: MealPlanORM,
        warnings: list[str] | None = None,
    ) -> MealPlanResponse:
        items: list[MealPlanItemResponse] = []
        meals: list[MealSlotResponse] = []

        for day in meal_plan.days:
            if day.slots:
                for slot in day.slots:
                    slot_dishes: list[MealSlotDishResponse] = []
                    for slot_dish in slot.dishes:
                        dish_name = (
                            slot_dish.dish.name
                            if slot_dish.dish
                            else str(slot_dish.dish_id)
                        )
                        items.append(
                            MealPlanItemResponse(
                                day_number=day.day_number,
                                meal_type=slot.meal_type,
                                dish_id=slot_dish.dish_id,
                                dish_name=dish_name,
                            )
                        )
                        slot_dishes.append(
                            MealSlotDishResponse(
                                id=slot_dish.id,
                                dish_id=slot_dish.dish_id,
                                dish_name=dish_name,
                            )
                        )

                    meals.append(
                        MealSlotResponse(
                            id=slot.id,
                            day_number=day.day_number,
                            meal_type=slot.meal_type,
                            dishes=slot_dishes,
                        )
                    )
                continue

            legacy_meals: dict[str, list[MealSlotDishResponse]] = {}
            for item in day.items:
                dish_name = item.dish.name if item.dish else str(item.dish_id)
                items.append(
                    MealPlanItemResponse(
                        day_number=day.day_number,
                        meal_type=item.meal_type,
                        dish_id=item.dish_id,
                        dish_name=dish_name,
                    )
                )
                legacy_meals.setdefault(item.meal_type, []).append(
                    MealSlotDishResponse(
                        id=f"legacy:{item.id}",
                        dish_id=item.dish_id,
                        dish_name=dish_name,
                    )
                )

            for meal_type, dishes in legacy_meals.items():
                meals.append(
                    MealSlotResponse(
                        id=f"legacy:{day.day_number}:{meal_type}",
                        day_number=day.day_number,
                        meal_type=meal_type,
                        dishes=dishes,
                    )
                )

        response_warnings = meal_plan.warnings if warnings is None else warnings
        return MealPlanResponse(
            id=meal_plan.id,
            project_id=meal_plan.project_id,
            name=meal_plan.name,
            participants=meal_plan.participants,
            days_count=meal_plan.days_count,
            items=items,
            meals=meals,
            warnings=list(response_warnings),
        )
