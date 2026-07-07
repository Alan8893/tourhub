from uuid import uuid4

from app.domain.workflows.purchase_checklist import PurchaseChecklistWorkflow, PurchaseChecklistStatus
from app.engines.shopping_list import ShoppingListResult
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list import PurchaseListORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class PurchaseChecklistService:
    """Application service for purchase checklist workflow."""

    def __init__(self, repository: PurchaseChecklistRepository, meal_plan_repository: MealPlanRepository | None = None, shopping_service: MealPlanShoppingService | None = None):
        self.repository = repository
        self.meal_plan_repository = meal_plan_repository
        self.shopping_service = shopping_service

    def get(self, checklist_id: str) -> PurchaseChecklistORM | None:
        return self.repository.get_by_id(checklist_id)

    def get_progress(self, checklist_id: str) -> dict:
        checklist = self.get(checklist_id)
        if not checklist:
            raise ValueError("Purchase checklist not found")
        total_items = len(checklist.items)
        checked_items = sum(1 for item in checklist.items if item.is_checked)
        return {
            "id": checklist.id,
            "status": checklist.status,
            "total_items": total_items,
            "checked_items": checked_items,
            "progress_percent": round((checked_items / total_items) * 100, 2) if total_items else 0,
        }

    def create_from_purchase_list(self, purchase_list: PurchaseListORM) -> PurchaseChecklistORM:
        checklist = PurchaseChecklistORM(id=str(uuid4()), meal_plan_id=purchase_list.meal_plan_id, status=PurchaseChecklistStatus.DRAFT.value)
        self.repository.add(checklist)
        for item in purchase_list.items:
            self.repository.add_item(PurchaseChecklistItemORM(id=str(uuid4()), checklist=checklist, product_id=item.product_id, required_quantity=item.required_quantity, purchased_quantity=0, unit=item.required_unit, is_checked=False))
        self.repository.commit()
        return checklist

    def create_from_meal_plan_id(self, meal_plan_id: str) -> PurchaseChecklistORM:
        if not self.meal_plan_repository:
            raise ValueError("Meal plan repository is required")
        meal_plan = self.meal_plan_repository.get_with_details(meal_plan_id)
        if not meal_plan:
            raise ValueError("Meal plan not found")
        return self.create_from_meal_plan(meal_plan)

    def create_from_meal_plan(self, meal_plan):
        if not self.shopping_service:
            raise ValueError("Shopping service is required")
        return self.create_from_shopping_list(meal_plan.id, self.shopping_service.calculate(meal_plan))

    def create_from_shopping_list(self, meal_plan_id: str, shopping_list: ShoppingListResult) -> PurchaseChecklistORM:
        checklist = PurchaseChecklistORM(id=str(uuid4()), meal_plan_id=meal_plan_id, status=PurchaseChecklistStatus.DRAFT.value)
        self.repository.add(checklist)
        for item in shopping_list.items:
            product = self.repository.get_product_by_name(item.product_name)
            if not product:
                raise ValueError(f"Product not found: {item.product_name}")
            self.repository.add_item(PurchaseChecklistItemORM(id=str(uuid4()), checklist=checklist, product_id=product.id, required_quantity=item.amount, purchased_quantity=0, unit=item.unit, is_checked=False))
        self.repository.commit()
        return checklist

    def update_item(self, item_id: str, checked: bool | None = None, purchased_quantity: float | None = None) -> PurchaseChecklistItemORM:
        item = self.repository.get_item_by_id(item_id)
        if not item:
            raise ValueError("Checklist item not found")
        if checked is not None:
            item.is_checked = checked
        if purchased_quantity is not None:
            item.purchased_quantity = purchased_quantity
        checklist = item.checklist
        current_status = checklist.status
        if all(current.is_checked for current in checklist.items):
            target_status = PurchaseChecklistStatus.COMPLETED.value
        elif any(current.is_checked for current in checklist.items):
            target_status = PurchaseChecklistStatus.IN_PROGRESS.value
        else:
            target_status = PurchaseChecklistStatus.DRAFT.value
        if current_status != target_status:
            checklist.status = PurchaseChecklistWorkflow.transition(current_status, target_status)
        self.repository.commit()
        return item
