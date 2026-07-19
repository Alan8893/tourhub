from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.database import get_db
from app.engines.documents.dto import GeneratedDocument
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectParticipantsUpdateRequest,
    ProjectRecipeGenerationModeUpdateRequest,
    ProjectResponse,
)
from app.modules.projects.service import Project, ProjectService
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.club_settings_service import ClubSettingsService
from app.services.document_appearance_settings_service import (
    DocumentAppearanceSettingsService,
)
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.project_document_package_service import ProjectDocumentPackageService
from app.services.project_document_service import ProjectDocumentService
from app.services.project_participant_recalculation_service import (
    ProjectParticipantRecalculationService,
)
from app.services.project_preparation_service import (
    ProjectPreparationResult,
    ProjectPreparationService,
)
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/projects", tags=["projects"])


def _project_response(project: Project | ProjectORM) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        name=project.name,
        participants=project.participants,
        days=project.days,
        start_date=project.start_date,
        first_meal=project.first_meal,
        last_meal=project.last_meal,
        recipe_generation_mode=project.recipe_generation_mode,
        status=project.status,
    )


@router.post("", response_model=ProjectResponse)
def create_project(
    request: ProjectCreateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    try:
        project = ProjectService(ProjectRepository(db), actor=actor).create_project(
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
    return _project_response(project)


@router.get("", response_model=ProjectListResponse)
def list_projects(db: Session = Depends(get_db)) -> ProjectListResponse:
    projects = ProjectRepository(db).list()
    return ProjectListResponse(items=[_project_response(project) for project in projects])


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    try:
        project = ProjectService(ProjectRepository(db)).get_project(project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _project_response(project)


@router.patch("/{project_id}/participants", response_model=ProjectResponse)
def update_project_participants(
    project_id: int,
    request: ProjectParticipantsUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    service = ProjectParticipantRecalculationService(
        db,
        MealPlanShoppingService(ShoppingListService(db)),
        actor=actor,
    )
    try:
        project = service.update_participants(project_id, request.participants)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _project_response(project)


@router.patch("/{project_id}/recipe-generation-mode", response_model=ProjectResponse)
def update_project_recipe_generation_mode(
    project_id: int,
    request: ProjectRecipeGenerationModeUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    try:
        project = ProjectService(
            ProjectRepository(db),
            actor=actor,
        ).update_recipe_generation_mode(
            project_id,
            request.recipe_generation_mode.value,
        )
    except ValueError as error:
        status_code = 404 if str(error) == "Project not found" else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    return _project_response(project)


@router.post("/{project_id}/prepare")
def prepare_project(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectPreparationResult:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        shopping_service = ShoppingListService(db)
        meal_plan_shopping_service = MealPlanShoppingService(shopping_service)
        meal_plan_repository = MealPlanRepository(db)
        preparation_service = ProjectPreparationService(
            PurchaseListService(
                PurchaseListRepository(db),
                meal_plan_repository,
                meal_plan_shopping_service,
            ),
            PurchaseChecklistService(
                PurchaseChecklistRepository(db),
                meal_plan_repository,
                meal_plan_shopping_service,
            ),
            EquipmentListService(
                EquipmentListRepository(db),
                meal_plan_repository,
            ),
            session=db,
            actor=actor,
        )
        return preparation_service.prepare_project(project)
    except ValueError as error:
        if str(error) == "Meal plan not found":
            raise HTTPException(status_code=404, detail=str(error)) from error
        raise HTTPException(status_code=400, detail=str(error)) from error


def _document_service(db: Session) -> ProjectDocumentService:
    return ProjectDocumentService(
        purchase_list_repository=PurchaseListRepository(db),
        equipment_list_repository=EquipmentListRepository(db),
        club_settings_service=ClubSettingsService(db),
        document_appearance_service=DocumentAppearanceSettingsService(db),
    )


def _download(document: GeneratedDocument) -> Response:
    return Response(
        content=document.content,
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )


def _prepared_document_error(error: ValueError) -> HTTPException | None:
    messages = {
        "Purchase list not found": "Project purchasing is not prepared",
        "Equipment list not found": "Project equipment is not prepared",
        "Meal plan not found": "Project menu is not prepared",
    }
    detail = messages.get(str(error))
    return HTTPException(status_code=409, detail=detail) if detail is not None else None


@router.get("/{project_id}/documents/purchase/{format}")
def generate_purchase_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    service = _document_service(db)
    generators = {
        "pdf": service.generate_purchase_pdf,
        "excel": service.generate_purchase_excel,
        "print": service.generate_purchase_print,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")
    try:
        return _download(generator(project))
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise


@router.get("/{project_id}/documents/equipment/{format}")
def generate_equipment_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    service = _document_service(db)
    generators = {
        "pdf": service.generate_equipment_pdf,
        "excel": service.generate_equipment_excel,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")
    try:
        return _download(generator(project))
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise


@router.get("/{project_id}/documents/consolidated/{format}")
def generate_consolidated_project_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    service = _document_service(db)
    generators = {
        "pdf": service.generate_consolidated_pdf,
        "excel": service.generate_consolidated_excel,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")
    try:
        return _download(generator(project))
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise


@router.get("/{project_id}/documents/package")
def generate_project_document_package(
    project_id: int,
    db: Session = Depends(get_db),
) -> Response:
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        document = ProjectDocumentPackageService(_document_service(db)).generate_package(
            project
        )
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise
    return _download(document)
