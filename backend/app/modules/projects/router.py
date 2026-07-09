from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreateRequest, ProjectResponse
from app.modules.projects.service import ProjectService
from app.services.project_document_package_service import ProjectDocumentPackageService
from app.services.project_document_service import ProjectDocumentService

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
    try:
        return ProjectService(ProjectRepository(db)).get_project(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{project_id}/documents/purchase/{format}")
def generate_purchase_document(project_id: int, format: str, db: Session = Depends(get_db)) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ProjectDocumentService()
    generators = {
        "pdf": service.generate_purchase_pdf,
        "excel": service.generate_purchase_excel,
        "print": service.generate_purchase_print,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")

    document = generator(project)
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )


@router.get("/{project_id}/documents/package")
def generate_project_document_package(project_id: int, db: Session = Depends(get_db)) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    document = ProjectDocumentPackageService().generate_package(project)
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )
