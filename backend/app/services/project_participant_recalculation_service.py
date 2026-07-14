from sqlalchemy.orm import Session

from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_purchasing_refresh_service import (
    MealPlanPurchasingRefreshService,
)
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
        self.purchasing_refresh_service = MealPlanPurchasingRefreshService(
            self.purchase_list_repository,
            self.checklist_repository,
            self.shopping_service,
        )

    def update_participants(self, project_id: int, participants: int) -> ProjectORM:
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")

        project = self.project_repository.get_by_id(project_id)
        if project is None:
            raise LookupError("Project not found")

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

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        self.session.refresh(project)
        return project
