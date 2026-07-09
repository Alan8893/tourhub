from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreateRequest, ProjectResponse
from app.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
def create_project(request: ProjectCreateRequest, db: Session = Depends(get_db)) -> ProjectResponse:
    try:
        project = ProjectService(ProjectRepository(db)).create_project(
            name=request.name,
            participants=request.participants,
            days=request.days,
            start_date=request.start_date,
            first_meal=request.first_meal,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return ProjectResponse(**project.__dict__)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    return ProjectService(ProjectRepository(db)).get_project(project_id)
