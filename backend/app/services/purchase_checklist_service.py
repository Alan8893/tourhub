from uuid import uuid4

from app.engines.shopping_list import ShoppingListResult
from app.models.meal_plan import MealPlanORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class PurchaseChecklistService:
    """Application service for purchase checklist workflow."""

    def __init__(
        self,
        repository: PurchaseChecklistRepository,
        shopping_service: MealPlanShoppingService | None = None,
    ):
        self.repository = repository
        self.shopping_service = shopping_service

    def create_from_meal_plan(
        self,
        meal_plan: MealPlanORM,
    ) -> PurchaseChecklistORM:
        if not self.shopping_service:
            raise ValueError("Shopping service is required")

        shopping_list = self.shopping_service.calculate(meal_plan)

        return self.create_from_shopping_list(
            meal_plan_id=meal_plan.id,
            shopping_list=shopping_list,
        )

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
                raise ValueError(
                    f"Product not found: {item.product_name}"
                )

            checklist_item = PurchaseChecklistItemORM(
                id=str(uuid4()),
                checklist=checklist,
                product_id=product.id,
                required_quantity=item.amount,
                purchased_quantity=0,
                unit=item.unit,
                is_checked=False,
            )
            self.repository.add_item(checklist_item)

        self.repository.commit()

        return checklist

    def get(
        self,
        checklist_id: str,
    ) -> PurchaseChecklistORM | None:
        return self.repository.get_by_id(checklist_id)

    def check_item(
        self,
        item: PurchaseChecklistItemORM,
        checked: bool,
    ) -> PurchaseChecklistItemORM:
        item.is_checked = checked
        return item
