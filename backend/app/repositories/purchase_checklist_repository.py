from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM


class PurchaseChecklistRepository:
    """Repository for purchase checklist persistence."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, checklist: PurchaseChecklistORM) -> None:
        self.session.add(checklist)

    def add_item(self, item: PurchaseChecklistItemORM) -> None:
        self.session.add(item)

    def get_product_by_name(self, product_name: str) -> ProductORM | None:
        return (
            self.session.query(ProductORM)
            .filter(ProductORM.name == product_name)
            .first()
        )

    def get_by_id(self, checklist_id: str) -> PurchaseChecklistORM | None:
        return (
            self.session.query(PurchaseChecklistORM)
            .filter(PurchaseChecklistORM.id == checklist_id)
            .first()
        )

    def get_by_meal_plan_id(self, meal_plan_id: str) -> PurchaseChecklistORM | None:
        return (
            self.session.query(PurchaseChecklistORM)
            .filter(PurchaseChecklistORM.meal_plan_id == meal_plan_id)
            .first()
        )

    def get_by_project_id(self, project_id: int) -> PurchaseChecklistORM | None:
        return (
            self.session.query(PurchaseChecklistORM)
            .filter(PurchaseChecklistORM.project_id == project_id)
            .first()
        )

    def get_item_by_id(self, item_id: str) -> PurchaseChecklistItemORM | None:
        return (
            self.session.query(PurchaseChecklistItemORM)
            .filter(PurchaseChecklistItemORM.id == item_id)
            .first()
        )

    def commit(self) -> None:
        self.session.flush()
        self.session.commit()
