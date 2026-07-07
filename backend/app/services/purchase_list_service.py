from uuid import uuid4

from app.engines.packaging import PackagedShoppingResult
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.repositories.purchase_list_repository import PurchaseListRepository


class PurchaseListService:
    """Application service for purchase list workflow."""

    def __init__(
        self,
        repository: PurchaseListRepository,
    ):
        self.repository = repository

    def create_from_packaged_shopping(
        self,
        meal_plan_id: str,
        shopping_result: PackagedShoppingResult,
    ) -> PurchaseListORM:
        purchase_list = PurchaseListORM(
            id=str(uuid4()),
            meal_plan_id=meal_plan_id,
            status="prepared",
        )

        self.repository.add(purchase_list)

        for item in shopping_result.items:
            self.repository.add_item(
                PurchaseListItemORM(
                    id=str(uuid4()),
                    purchase_list=purchase_list,
                    product_id=self._resolve_product_id(
                        item.product_name
                    ),
                    required_quantity=item.amount,
                    required_unit=item.unit,
                    package_size=item.package_size,
                    package_unit=item.unit,
                    packages_count=item.packages,
                )
            )

        self.repository.commit()
        return purchase_list

    def get(
        self,
        purchase_list_id: str,
    ) -> PurchaseListORM | None:
        return self.repository.get_by_id(purchase_list_id)

    def _resolve_product_id(
        self,
        product_name: str,
    ) -> str:
        product = self.repository.get_product_by_id(product_name)

        if not product:
            raise ValueError(
                f"Product not found: {product_name}"
            )

        return product.id
