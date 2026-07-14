from uuid import uuid4

from app.domain.workflows.purchase_checklist import PurchaseChecklistStatus
from app.models.meal_plan import MealPlanORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class MealPlanPurchasingRefreshService:
    """Refresh persisted purchasing projections from the current meal plan."""

    def __init__(
        self,
        purchase_list_repository: PurchaseListRepository,
        checklist_repository: PurchaseChecklistRepository,
        shopping_service: MealPlanShoppingService,
    ) -> None:
        self.purchase_list_repository = purchase_list_repository
        self.checklist_repository = checklist_repository
        self.shopping_service = shopping_service

    def refresh(self, meal_plan: MealPlanORM) -> None:
        self._refresh_purchase_list(meal_plan)
        self._refresh_checklist(meal_plan)

    def _refresh_purchase_list(self, meal_plan: MealPlanORM) -> None:
        purchase_list = self.purchase_list_repository.get_by_meal_plan_id(str(meal_plan.id))
        if purchase_list is None:
            return

        result = self.shopping_service.calculate_packaged(meal_plan)
        purchase_list.items.clear()

        for item in result.items:
            product = self.purchase_list_repository.get_product_by_name(item.product_name)
            if product is None:
                raise ValueError(f"Product not found: {item.product_name}")

            purchase_list.items.append(
                PurchaseListItemORM(
                    id=str(uuid4()),
                    product_id=product.id,
                    required_quantity=item.amount,
                    required_unit=item.unit,
                    package_size=item.package_size,
                    package_unit=item.unit,
                    packages_count=item.packages,
                )
            )

    def _refresh_checklist(self, meal_plan: MealPlanORM) -> None:
        checklist = self.checklist_repository.get_by_meal_plan_id(str(meal_plan.id))
        if checklist is None:
            return

        previous_state = {
            item.product_id: (
                item.purchased_quantity,
                item.is_checked,
                item.note,
            )
            for item in checklist.items
        }
        result = self.shopping_service.calculate(meal_plan)
        checklist.items.clear()

        for item in result.items:
            product = self.checklist_repository.get_product_by_name(item.product_name)
            if product is None:
                raise ValueError(f"Product not found: {item.product_name}")

            purchased_quantity, is_checked, note = previous_state.get(
                product.id,
                (0, False, None),
            )
            checklist.items.append(
                PurchaseChecklistItemORM(
                    id=str(uuid4()),
                    product_id=product.id,
                    required_quantity=item.amount,
                    purchased_quantity=purchased_quantity,
                    unit=item.unit,
                    is_checked=is_checked,
                    note=note,
                )
            )

        if checklist.items and all(item.is_checked for item in checklist.items):
            checklist.status = PurchaseChecklistStatus.COMPLETED.value
        elif any(item.is_checked for item in checklist.items):
            checklist.status = PurchaseChecklistStatus.IN_PROGRESS.value
        else:
            checklist.status = PurchaseChecklistStatus.DRAFT.value
