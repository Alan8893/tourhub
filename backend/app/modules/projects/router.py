from fastapi import APIRouter

from app.modules.projects.schemas import ProjectResponse
from app.modules.projects.service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])

service = ProjectService()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int) -> ProjectResponse:
    return service.get_project(project_id)
