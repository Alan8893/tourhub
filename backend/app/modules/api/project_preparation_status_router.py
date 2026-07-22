from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.database import get_db
from app.core.project_access import ProjectAccessPolicy
from app.models.user import UserORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.project_preparation_service import ProjectPreparationResult
from app.services.project_preparation_status_service import ProjectPreparationStatusService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{project_id}/preparation", response_model=None)
def get_project_preparation(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectPreparationResult:
    ProjectAccessPolicy.require_visible(db, project_id, actor)
    return ProjectPreparationStatusService(
        MealPlanRepository(db),
        PurchaseListRepository(db),
        PurchaseChecklistRepository(db),
        EquipmentListRepository(db),
    ).get(project_id)
