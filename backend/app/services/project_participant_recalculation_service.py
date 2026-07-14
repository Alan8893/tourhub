from uuid import uuid4

from sqlalchemy.orm import Session

from app.domain.workflows.purchase_checklist import PurchaseChecklistStatus
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class ProjectParticipantRecalculationService:
    """Update participant count and refresh derived purchasing data atomically."""

    def __init__(
        self,
        session: Session,
        shopping_service: MealPlanShoppingService,
    ) -> None:
        self.session = session
        self.shopping_service = shopping_service
        self.project_repository = ProjectRepository(session)
        self.meal_plan_repository = MealPlanRepository(session)
        self.purchase_list_repository = PurchaseListRepository(session)
        self.checklist_repository = PurchaseChecklistRepository(session)

    def update_participants(self, project_id: int, participants: int):
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")

        project = self.project_repository.get_by_id(project_id)
        if project is None:
            raise LookupError("Project not found")

        project.participants = participants

        meal_plan = self.meal_plan_repository.get_by_project_id(project_id)
        if meal_plan is not None:
            detailed_meal_plan = self.meal_plan_repository.get_with_details(
                str(meal_plan.id)
            )
            if detailed_meal_plan is None:
                raise LookupError("Meal plan not found")

            detailed_meal_plan.participants = participants
            self._refresh_purchase_list(detailed_meal_plan)
            self._refresh_checklist(detailed_meal_plan)

        self.session.commit()
        self.session.refresh(project)
        return project

    def _refresh_purchase_list(self, meal_plan) -> None:
        purchase_list = self.purchase_list_repository.get_by_meal_plan_id(
            str(meal_plan.id)
        )
        if purchase_list is None:
            return

        result = self.shopping_service.calculate_packaged(meal_plan)
        purchase_list.items.clear()

        for item in result.items:
            product = self.purchase_list_repository.get_product_by_name(
                item.product_name
            )
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

    def _refresh_checklist(self, meal_plan) -> None:
        checklist = self.checklist_repository.get_by_meal_plan_id(
            str(meal_plan.id)
        )
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
            product = self.checklist_repository.get_product_by_name(
                item.product_name
            )
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
