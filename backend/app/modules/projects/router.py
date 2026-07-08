from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import ProjectResponse
from app.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    service = ProjectService(ProjectRepository(db))
    return service.get_project(project_id)
