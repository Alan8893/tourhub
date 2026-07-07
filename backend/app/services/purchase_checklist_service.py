from uuid import uuid4

from app.engines.shopping_list import ShoppingListResult
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class PurchaseChecklistService:
    """Application service for purchase checklist workflow."""

    def __init__(
        self,
        repository: PurchaseChecklistRepository,
        meal_plan_repository: MealPlanRepository | None = None,
        shopping_service: MealPlanShoppingService | None = None,
    ):
        self.repository = repository
        self.meal_plan_repository = meal_plan_repository
        self.shopping_service = shopping_service

    def create_from_meal_plan_id(
        self,
        meal_plan_id: str,
    ) -> PurchaseChecklistORM:
        if not self.meal_plan_repository:
            raise ValueError("Meal plan repository is required")

        meal_plan = self.meal_plan_repository.get_with_details(meal_plan_id)

        if not meal_plan:
            raise ValueError("Meal plan not found")

        return self.create_from_meal_plan(meal_plan)

    def create_from_meal_plan(self, meal_plan):
        if not self.shopping_service:
            raise ValueError("Shopping service is required")

        shopping_list = self.shopping_service.calculate(meal_plan)
        return self.create_from_shopping_list(meal_plan.id, shopping_list)

    def create_from_shopping_list(
        self,
        meal_plan_id: str,
        shopping_list: ShoppingListResult,
    ) -> PurchaseChecklistORM:
        checklist = PurchaseChecklistORM(
            id=str(uuid4()),
            meal_plan_id=meal_plan_id,
            status="draft",
        )

        self.repository.add(checklist)

        for item in shopping_list.items:
            product = self.repository.get_product_by_name(item.product_name)

            if not product:
                raise ValueError(f"Product not found: {item.product_name}")

            self.repository.add_item(
                PurchaseChecklistItemORM(
                    id=str(uuid4()),
                    checklist=checklist,
                    product_id=product.id,
                    required_quantity=item.amount,
                    purchased_quantity=0,
                    unit=item.unit,
                    is_checked=False,
                )
            )

        self.repository.commit()
        return checklist

    def get(self, checklist_id: str) -> PurchaseChecklistORM | None:
        return self.repository.get_by_id(checklist_id)

    def update_item(
        self,
        item_id: str,
        checked: bool | None = None,
        purchased_quantity: float | None = None,
    ) -> PurchaseChecklistItemORM:
        item = self.repository.get_item_by_id(item_id)

        if not item:
            raise ValueError("Checklist item not found")

        if checked is not None:
            item.is_checked = checked

        if purchased_quantity is not None:
            item.purchased_quantity = purchased_quantity

        checklist = item.checklist

        if all(current.is_checked for current in checklist.items):
            checklist.status = "completed"
        elif any(current.is_checked for current in checklist.items):
            checklist.status = "in_progress"
        else:
            checklist.status = "draft"

        self.repository.commit()
        return item
