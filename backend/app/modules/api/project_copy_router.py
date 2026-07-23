from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.session import get_session
from app.models.user import UserORM
from app.schemas.project_copy import ProjectCopyRequest, ProjectCopyResponse
from app.services.project_copy_service import ProjectCopyService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/{project_id}/copy", response_model=ProjectCopyResponse)
def copy_project(
    project_id: int,
    request: ProjectCopyRequest,
    session: Session = Depends(get_session),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectCopyResponse:
    try:
        result = ProjectCopyService(session, actor=actor).copy_project(
            project_id,
            name=request.name,
            participants=request.participants,
            days=request.days,
            start_date=request.start_date,
            first_meal=request.first_meal,
            last_meal=request.last_meal,
            recipe_generation_mode=request.recipe_generation_mode.value,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return ProjectCopyResponse(**result.__dict__)
