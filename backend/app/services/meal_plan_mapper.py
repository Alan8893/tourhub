from app.models.meal_plan import MealPlanORM

from app.schemas.meal_plan import (
    MealPlanItemResponse,
    MealPlanResponse,
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
        """
        Convert ORM meal plan to response DTO.
        """

        items: list[MealPlanItemResponse] = []

        for day in meal_plan.days:
            for item in day.items:
                items.append(
                    MealPlanItemResponse(
                        day_number=day.day_number,
                        meal_type=item.meal_type,
                        dish_id=item.dish_id,
                        dish_name=(
                            item.dish.name
                            if item.dish
                            else item.dish_id
                        ),
                    )
                )

        return MealPlanResponse(
            id=meal_plan.id,
            project_id=meal_plan.project_id,
            name=meal_plan.name,
            participants=meal_plan.participants,
            days_count=meal_plan.days_count,
            items=items,
            warnings=warnings or [],
        )
