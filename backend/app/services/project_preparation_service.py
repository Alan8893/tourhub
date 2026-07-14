from dataclasses import dataclass

from app.modules.projects.models.project import ProjectORM
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService


@dataclass(frozen=True)
class ProjectPreparationResult:
    project_id: int
    meal_plan_id: str
    purchase_list_id: str
    purchase_checklist_id: str


class ProjectPreparationService:
    """Coordinates the full project preparation workflow."""

    def __init__(
        self,
        purchase_list_service: PurchaseListService,
        purchase_checklist_service: PurchaseChecklistService,
    ) -> None:
        self.purchase_list_service = purchase_list_service
        self.purchase_checklist_service = purchase_checklist_service

    def prepare_project(self, project: ProjectORM) -> ProjectPreparationResult:
        if not project.meal_plans:
            raise ValueError("Meal plan not found")

        meal_plan = project.meal_plans[0]

        purchase_list = self.purchase_list_service.create_from_meal_plan_id(
            str(meal_plan.id),
            project_id=project.id,
        )

        checklist = self.purchase_checklist_service.create_from_purchase_list(
            purchase_list,
        )

        return ProjectPreparationResult(
            project_id=project.id,
            meal_plan_id=str(meal_plan.id),
            purchase_list_id=str(purchase_list.id),
            purchase_checklist_id=str(checklist.id),
        )
