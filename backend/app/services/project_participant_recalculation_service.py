from sqlalchemy.orm import Session

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.audit_service import AuditService
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)
from app.services.meal_plan_shopping_service import MealPlanShoppingService


class ProjectParticipantRecalculationService:
    """Update participant count and refresh derived project data atomically."""

    def __init__(
        self,
        session: Session,
        shopping_service: MealPlanShoppingService,
        actor: UserORM | None = None,
    ) -> None:
        self.session = session
        self.shopping_service = shopping_service
        self.actor = actor
        self.project_repository = ProjectRepository(session)
        self.meal_plan_repository = MealPlanRepository(session)
        self.purchase_list_repository = PurchaseListRepository(session)
        self.checklist_repository = PurchaseChecklistRepository(session)
        self.purchasing_refresh_service = MealPlanPurchasingRefreshService(
            self.purchase_list_repository,
            self.checklist_repository,
            self.shopping_service,
        )
        self.equipment_list_service = EquipmentListService(
            EquipmentListRepository(session),
            self.meal_plan_repository,
        )

    def update_participants(self, project_id: int, participants: int) -> ProjectORM:
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")

        project = self.project_repository.get_by_id(project_id)
        if project is None:
            raise LookupError("Project not found")
        if project.participants == participants:
            return project

        before = self._snapshot(project)
        meal_plan_refreshed = False
        equipment_refreshed = False
        try:
            project.participants = participants

            meal_plan = self.meal_plan_repository.get_by_project_id(project_id)
            if meal_plan is not None:
                detailed_meal_plan = self.meal_plan_repository.get_with_details(
                    str(meal_plan.id)
                )
                if detailed_meal_plan is None:
                    raise LookupError("Meal plan not found")

                detailed_meal_plan.participants = participants
                self.purchasing_refresh_service.refresh(detailed_meal_plan)
                meal_plan_refreshed = True
                equipment_refreshed = (
                    self.equipment_list_service.refresh_existing(detailed_meal_plan)
                    is not None
                )

            if self.actor is not None:
                AuditService(self.session).record(
                    actor=self.actor,
                    action="project_participants_updated",
                    entity_type="project",
                    entity_id=project.id,
                    before=before,
                    after=self._snapshot(project),
                    context={
                        "changed_fields": ["participants"],
                        "meal_plan_refreshed": meal_plan_refreshed,
                        "equipment_refreshed": equipment_refreshed,
                    },
                )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        self.session.refresh(project)
        return project

    @staticmethod
    def _snapshot(project: ProjectORM) -> dict[str, object]:
        return {
            "name": project.name,
            "participants": project.participants,
            "days": project.days,
            "recipe_generation_mode": project.recipe_generation_mode,
            "status": project.status,
        }
