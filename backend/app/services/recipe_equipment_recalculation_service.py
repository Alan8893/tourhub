from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dish import DishORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.equipment_list_service import EquipmentListService


class RecipeEquipmentRecalculationService:
    """Refresh prepared equipment lists affected by one recipe requirement change."""

    def __init__(self, session: Session) -> None:
        self.session = session
        meal_plan_repository = MealPlanRepository(session)
        self.meal_plan_repository = meal_plan_repository
        self.equipment_service = EquipmentListService(
            EquipmentListRepository(session),
            meal_plan_repository,
        )

    def refresh_affected_meal_plans(self, recipe_id: str) -> None:
        statement = (
            select(MealPlanDayORM.meal_plan_id)
            .join(MealSlotORM, MealSlotORM.meal_plan_day_id == MealPlanDayORM.id)
            .join(MealSlotDishORM, MealSlotDishORM.meal_slot_id == MealSlotORM.id)
            .join(DishORM, DishORM.id == MealSlotDishORM.dish_id)
            .where(DishORM.recipe_id == recipe_id)
            .distinct()
        )
        meal_plan_ids = list(self.session.scalars(statement).all())

        for meal_plan_id in meal_plan_ids:
            meal_plan = self.meal_plan_repository.get_with_details(str(meal_plan_id))
            if meal_plan is None:
                raise LookupError("Meal plan not found")
            self.equipment_service.refresh_existing(meal_plan)
