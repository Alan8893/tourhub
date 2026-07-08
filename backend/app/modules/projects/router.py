from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import ProjectResponse
from app.modules.projects.service import ProjectService
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.purchase_checklist import PurchaseChecklistResponse
from app.services.project_preparation_schema import ProjectPreparationResponse
from app.services.project_preparation_service import ProjectPreparationService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    service = ProjectService(ProjectRepository(db))
    return service.get_project(project_id)


@router.post("/{project_id}/prepare", response_model=ProjectPreparationResponse)
def prepare_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectPreparationResponse:
    project = ProjectRepository(db).get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ProjectPreparationService(
        purchase_list_service=PurchaseListService(
            PurchaseListRepository(db)
        ),
        purchase_checklist_service=PurchaseChecklistService(
            PurchaseChecklistRepository(db)
        ),
    )

    try:
        result = service.prepare_project(project)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return ProjectPreparationResponse(
        project_id=result.project_id,
        meal_plan_id=result.meal_plan_id,
        purchase_list_id=result.purchase_list_id,
        purchase_checklist_id=result.purchase_checklist_id,
    )
