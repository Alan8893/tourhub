from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectParticipantsUpdateRequest,
    ProjectResponse,
)
from app.modules.projects.service import ProjectService
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.project_document_package_service import ProjectDocumentPackageService
from app.services.project_document_service import ProjectDocumentService
from app.services.project_participant_recalculation_service import (
    ProjectParticipantRecalculationService,
)
from app.services.project_preparation_service import ProjectPreparationService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService
from app.services.shopping_list_service import ShoppingListService

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
            last_meal=request.last_meal,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return ProjectResponse(**project.__dict__)


@router.get("", response_model=ProjectListResponse)
def list_projects(db: Session = Depends(get_db)) -> ProjectListResponse:
    projects = ProjectRepository(db).list()
    return ProjectListResponse(
        items=[
            ProjectResponse(
                id=project.id,
                name=project.name,
                participants=project.participants,
                days=project.days,
                start_date=project.start_date,
                first_meal=project.first_meal,
                last_meal=project.last_meal,
                status=project.status,
            )
            for project in projects
        ]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    try:
        return ProjectService(ProjectRepository(db)).get_project(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/{project_id}/participants", response_model=ProjectResponse)
def update_project_participants(
    project_id: int,
    request: ProjectParticipantsUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectResponse:
    service = ProjectParticipantRecalculationService(
        db,
        MealPlanShoppingService(ShoppingListService(db)),
    )

    try:
        project = service.update_participants(project_id, request.participants)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return ProjectResponse(
        id=project.id,
        name=project.name,
        participants=project.participants,
        days=project.days,
        start_date=project.start_date,
        first_meal=project.first_meal,
        last_meal=project.last_meal,
        status=project.status,
    )


@router.post("/{project_id}/prepare")
def prepare_project(project_id: int, db: Session = Depends(get_db)):
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        shopping_service = ShoppingListService(db)
        meal_plan_shopping_service = MealPlanShoppingService(shopping_service)

        preparation_service = ProjectPreparationService(
            PurchaseListService(
                PurchaseListRepository(db),
                MealPlanRepository(db),
                meal_plan_shopping_service,
            ),
            PurchaseChecklistService(
                PurchaseChecklistRepository(db),
                MealPlanRepository(db),
                meal_plan_shopping_service,
            ),
        )

        return preparation_service.prepare_project(project)
    except ValueError as error:
        if str(error) == "Meal plan not found":
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{project_id}/documents/purchase/{format}")
def generate_purchase_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    service = ProjectDocumentService(
        purchase_list_repository=PurchaseListRepository(db),
    )
    generators = {
        "pdf": service.generate_purchase_pdf,
        "excel": service.generate_purchase_excel,
        "print": service.generate_purchase_print,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")

    try:
        document = generator(project)
    except ValueError as error:
        if str(error) == "Purchase list not found":
            raise HTTPException(
                status_code=409,
                detail="Project purchasing is not prepared",
            ) from error
        raise

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

    document_service = ProjectDocumentService(
        purchase_list_repository=PurchaseListRepository(db),
    )
    try:
        document = ProjectDocumentPackageService(document_service).generate_package(project)
    except ValueError as error:
        if str(error) == "Purchase list not found":
            raise HTTPException(
                status_code=409,
                detail="Project purchasing is not prepared",
            ) from error
        raise

    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )
