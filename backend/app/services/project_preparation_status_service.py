from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.project_preparation_service import ProjectPreparationResult


class ProjectPreparationStatusService:
    """Read persisted preparation state without mutating project documents."""

    def __init__(
        self,
        meal_plan_repository: MealPlanRepository,
        purchase_list_repository: PurchaseListRepository,
        purchase_checklist_repository: PurchaseChecklistRepository,
        equipment_list_repository: EquipmentListRepository,
    ) -> None:
        self.meal_plan_repository = meal_plan_repository
        self.purchase_list_repository = purchase_list_repository
        self.purchase_checklist_repository = purchase_checklist_repository
        self.equipment_list_repository = equipment_list_repository

    def get(self, project_id: int) -> ProjectPreparationResult:
        meal_plan = self.meal_plan_repository.get_by_project_id(project_id)
        purchase_list = self.purchase_list_repository.get_by_project_id(project_id)
        purchase_checklist = self.purchase_checklist_repository.get_by_project_id(project_id)
        equipment_list = self.equipment_list_repository.get_by_project_id(project_id)

        return ProjectPreparationResult(
            project_id=project_id,
            meal_plan_id=str(meal_plan.id) if meal_plan is not None else "",
            purchase_list_id=str(purchase_list.id) if purchase_list is not None else "",
            purchase_checklist_id=(
                str(purchase_checklist.id) if purchase_checklist is not None else ""
            ),
            equipment_list_id=(
                str(equipment_list.id) if equipment_list is not None else ""
            ),
        )
