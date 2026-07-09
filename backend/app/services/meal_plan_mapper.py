from collections import defaultdict

from app.models.meal_plan import MealPlanORM

from app.schemas.meal_plan import (
    MealPlanItemResponse,
    MealPlanResponse,
    MealSlotResponse,
)


class MealPlanMapper:
    """
    Maps MealPlan ORM entities to API schemas.
    """

    @staticmethod
    def to_response(
        meal_plan: MealPlanORM,
        warnings: list[str] | None = None,
    ) -> MealPlanResponse:
        items: list[MealPlanItemResponse] = []
        meals_map: dict[tuple[int, str], list[MealPlanItemResponse]] = defaultdict(list)

        for day in meal_plan.days:
            # Legacy MealPlanItem support
            for item in day.items:
                response_item = MealPlanItemResponse(
                    day_number=day.day_number,
                    meal_type=item.meal_type,
                    dish_id=item.dish_id,
                    dish_name=(
                        item.dish.name
                        if item.dish
                        else item.dish_id
                    ),
                )

                items.append(response_item)
                meals_map[(day.day_number, item.meal_type)].append(response_item)

            # New MealSlot support
            for slot in day.slots:
                slot_items: list[MealPlanItemResponse] = []

                for slot_dish in slot.dishes:
                    response_item = MealPlanItemResponse(
                        day_number=day.day_number,
                        meal_type=slot.meal_type,
                        dish_id=slot_dish.dish_id,
                        dish_name=(
                            slot_dish.dish.name
                            if slot_dish.dish
                            else slot_dish.dish_id
                        ),
                    )

                    slot_items.append(response_item)
                    items.append(response_item)

                meals_map[(day.day_number, slot.meal_type)] = slot_items

        meals = [
            MealSlotResponse(
                day_number=day_number,
                meal_type=meal_type,
                dishes=dishes,
            )
            for (day_number, meal_type), dishes in meals_map.items()
        ]

        return MealPlanResponse(
            id=meal_plan.id,
            project_id=meal_plan.project_id,
            name=meal_plan.name,
            participants=meal_plan.participants,
            days_count=meal_plan.days_count,
            items=items,
            meals=meals,
            warnings=warnings or [],
        )
