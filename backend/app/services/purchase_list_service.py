from typing import TypedDict
from uuid import uuid4

from app.domain.workflows.purchase_list import PurchaseListStatus
from app.engines.documents.dto import PurchaseDocumentDTO
from app.engines.packaging import PackagedShoppingResult
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.document_mapper import PurchaseDocumentMapper
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class PurchaseListSummary(TypedDict):
    id: str
    status: str
    items_total: int
    packages_total: int


class PurchaseListService:
    """Application service for purchase list workflow."""

    def __init__(
        self,
        repository: PurchaseListRepository,
        meal_plan_repository: MealPlanRepository | None = None,
        shopping_service: MealPlanShoppingService | None = None,
        document_mapper: PurchaseDocumentMapper | None = None,
    ) -> None:
        self.repository = repository
        self.meal_plan_repository = meal_plan_repository
        self.shopping_service = shopping_service
        self.document_mapper = document_mapper or PurchaseDocumentMapper()

    def create_from_meal_plan_id(
        self,
        meal_plan_id: str,
        project_id: int | None = None,
        *,
        commit: bool = True,
    ) -> PurchaseListORM:
        if not self.meal_plan_repository:
            raise ValueError("Meal plan repository is required")

        meal_plan = self.meal_plan_repository.get_with_details(meal_plan_id)

        if not meal_plan:
            raise ValueError("Meal plan not found")

        if project_id is None:
            project_id = meal_plan.project_id

        if not self.shopping_service:
            raise ValueError("Shopping service is required")

        return self.create_from_packaged_shopping(
            meal_plan_id,
            self.shopping_service.calculate_packaged(meal_plan),
            project_id=project_id,
            commit=commit,
        )

    def create_from_packaged_shopping(
        self,
        meal_plan_id: str,
        shopping_result: PackagedShoppingResult,
        project_id: int | None = None,
        *,
        commit: bool = True,
    ) -> PurchaseListORM:
        purchase_list = PurchaseListORM(
            id=str(uuid4()),
            meal_plan_id=meal_plan_id,
            project_id=project_id,
            status=PurchaseListStatus.PREPARED.value,
        )

        self.repository.add(purchase_list)

        for item in shopping_result.items:
            self.repository.add_item(
                PurchaseListItemORM(
                    id=str(uuid4()),
                    purchase_list=purchase_list,
                    product_id=self._resolve_product_id(item.product_name),
                    required_quantity=item.amount,
                    required_unit=item.unit,
                    package_size=item.package_size,
                    package_unit=item.unit,
                    packages_count=item.packages,
                )
            )

        self._finish_write(commit=commit)
        return purchase_list

    def get(self, purchase_list_id: str) -> PurchaseListORM | None:
        return self.repository.get_by_id(purchase_list_id)

    def update_responsible_person(
        self,
        purchase_list_id: str,
        responsible_person: str | None,
    ) -> PurchaseListORM:
        purchase_list = self.get(purchase_list_id)
        if not purchase_list:
            raise ValueError("Purchase list not found")

        normalized = responsible_person.strip() if responsible_person else None
        purchase_list.responsible_person = normalized or None
        self.repository.commit()
        return purchase_list

    def get_summary(self, purchase_list_id: str) -> PurchaseListSummary:
        purchase_list = self.get(purchase_list_id)

        if not purchase_list:
            raise ValueError("Purchase list not found")

        return {
            "id": purchase_list.id,
            "status": purchase_list.status,
            "items_total": len(purchase_list.items),
            "packages_total": sum(item.packages_count for item in purchase_list.items),
        }

    def create_document_dto(self, purchase_list: PurchaseListORM) -> PurchaseDocumentDTO:
        return self.document_mapper.to_dto(purchase_list)

    def _resolve_product_id(self, product_name: str) -> str:
        product = self.repository.get_product_by_name(product_name)

        if not product:
            raise ValueError(f"Product not found: {product_name}")

        return product.id

    def _finish_write(self, *, commit: bool) -> None:
        if commit:
            self.repository.commit()
        else:
            self.repository.flush()
