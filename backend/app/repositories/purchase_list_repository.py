from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM


class PurchaseListRepository:
    """Repository for purchase list persistence."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, purchase_list: PurchaseListORM) -> None:
        self.session.add(purchase_list)

    def add_item(self, item: PurchaseListItemORM) -> None:
        self.session.add(item)

    def get_by_id(self, purchase_list_id: str) -> PurchaseListORM | None:
        return (
            self.session.query(PurchaseListORM)
            .filter(PurchaseListORM.id == purchase_list_id)
            .first()
        )

    def get_by_project_id(
        self,
        project_id: int,
    ) -> PurchaseListORM | None:
        return (
            self.session.query(PurchaseListORM)
            .filter(PurchaseListORM.project_id == project_id)
            .first()
        )

    def get_by_meal_plan_id(
        self,
        meal_plan_id: str,
    ) -> PurchaseListORM | None:
        return (
            self.session.query(PurchaseListORM)
            .filter(PurchaseListORM.meal_plan_id == meal_plan_id)
            .first()
        )

    def get_product_by_id(
        self,
        product_id: str,
    ) -> ProductORM | None:
        return (
            self.session.query(ProductORM)
            .filter(ProductORM.id == product_id)
            .first()
        )

    def get_product_by_name(
        self,
        product_name: str,
    ) -> ProductORM | None:
        return (
            self.session.query(ProductORM)
            .filter(ProductORM.name == product_name)
            .first()
        )

    def commit(self) -> None:
        self.session.flush()
        self.session.commit()
