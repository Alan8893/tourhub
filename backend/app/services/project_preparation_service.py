from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.services.audit_service import AuditService
from app.services.equipment_list_service import EquipmentListService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService


@dataclass(frozen=True)
class ProjectPreparationResult:
    project_id: int
    meal_plan_id: str
    purchase_list_id: str
    purchase_checklist_id: str
    equipment_list_id: str


class ProjectPreparationService:
    """Coordinates the full project preparation workflow."""

    def __init__(
        self,
        purchase_list_service: PurchaseListService,
        purchase_checklist_service: PurchaseChecklistService,
        equipment_list_service: EquipmentListService,
        session: Session | None = None,
        actor: UserORM | None = None,
    ) -> None:
        self.purchase_list_service = purchase_list_service
        self.purchase_checklist_service = purchase_checklist_service
        self.equipment_list_service = equipment_list_service
        self.session = session
        self.actor = actor

    def prepare_project(self, project: ProjectORM) -> ProjectPreparationResult:
        if not project.meal_plans:
            raise ValueError("Meal plan not found")

        meal_plan = project.meal_plans[0]
        meal_plan_id = str(meal_plan.id)
        before = self._snapshot(project, meal_plan_id=meal_plan_id)

        try:
            purchase_list = self.purchase_list_service.create_from_meal_plan_id(
                meal_plan_id,
                project_id=project.id,
                commit=self.session is None,
            )
            checklist = self.purchase_checklist_service.create_from_purchase_list(
                purchase_list,
                commit=self.session is None,
            )
            equipment_list = self.equipment_list_service.create_from_meal_plan_id(
                meal_plan_id,
                project_id=project.id,
                commit=self.session is None,
            )

            result = ProjectPreparationResult(
                project_id=project.id,
                meal_plan_id=meal_plan_id,
                purchase_list_id=str(purchase_list.id),
                purchase_checklist_id=str(checklist.id),
                equipment_list_id=str(equipment_list.id),
            )

            if self.session is not None:
                if self.actor is not None:
                    AuditService(self.session).record(
                        actor=self.actor,
                        action="project_prepared",
                        entity_type="project",
                        entity_id=project.id,
                        before=before,
                        after={
                            **before,
                            "purchase_list_count": before["purchase_list_count"] + 1,
                            "purchase_checklist_count": (
                                before["purchase_checklist_count"] + 1
                            ),
                            "equipment_list_id": result.equipment_list_id,
                        },
                        context={
                            "meal_plan_id": result.meal_plan_id,
                            "purchase_list_id": result.purchase_list_id,
                            "purchase_checklist_id": result.purchase_checklist_id,
                            "equipment_list_id": result.equipment_list_id,
                        },
                    )
                self.session.commit()
            return result
        except Exception:
            if self.session is not None:
                self.session.rollback()
            raise

    @staticmethod
    def _snapshot(project: ProjectORM, *, meal_plan_id: str) -> dict[str, object]:
        return {
            "name": project.name,
            "status": project.status,
            "meal_plan_id": meal_plan_id,
            "purchase_list_count": len(project.purchase_lists),
            "purchase_checklist_count": len(project.purchase_checklists),
            "equipment_list_id": None,
        }
