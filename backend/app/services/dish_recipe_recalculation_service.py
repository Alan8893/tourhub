from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.shopping_list_service import ShoppingListService


class DishRecipeRecalculationService:
    def __init__(self, session: Session):
        self.session = session

    def refresh_affected_meal_plans(self, dish_id: str) -> None:
        statement = (
            select(MealPlanDayORM.meal_plan_id)
            .join(MealSlotORM, MealSlotORM.meal_plan_day_id == MealPlanDayORM.id)
            .join(MealSlotDishORM, MealSlotDishORM.meal_slot_id == MealSlotORM.id)
            .where(MealSlotDishORM.dish_id == dish_id)
            .distinct()
        )
        meal_plan_ids = list(self.session.scalars(statement).all())
        meal_plan_repository = MealPlanRepository(self.session)
        refresh_service = MealPlanPurchasingRefreshService(
            PurchaseListRepository(self.session),
            PurchaseChecklistRepository(self.session),
            MealPlanShoppingService(ShoppingListService(self.session)),
        )

        for meal_plan_id in meal_plan_ids:
            meal_plan = meal_plan_repository.get_with_details(str(meal_plan_id))
            if meal_plan is None:
                raise LookupError("Meal plan not found")
            refresh_service.refresh(meal_plan)
