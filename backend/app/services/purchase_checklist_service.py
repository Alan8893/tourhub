from uuid import uuid4

from app.engines.shopping_list import ShoppingListResult
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.repositories.purchase_checklist_repository import (
    PurchaseChecklistRepository,
)


class PurchaseChecklistService:
    """Application service for purchase checklist workflow."""

    def __init__(
        self,
        repository: PurchaseChecklistRepository,
    ):
        self.repository = repository

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
            checklist_item = PurchaseChecklistItemORM(
                id=str(uuid4()),
                checklist=checklist,
                product_id=item.product_name,
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
