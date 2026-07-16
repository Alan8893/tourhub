from app.models.meal_plan import MealPlanORM
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)


class MealPlanDerivedRefreshService:
    """Refresh persisted projections derived from the current meal plan."""

    def __init__(
        self,
        purchasing_service: MealPlanPurchasingRefreshService,
        equipment_service: EquipmentListService,
    ) -> None:
        self.purchasing_service = purchasing_service
        self.equipment_service = equipment_service

    def refresh(self, meal_plan: MealPlanORM) -> None:
        self.purchasing_service.refresh(meal_plan)
        self.equipment_service.refresh_existing(meal_plan)
