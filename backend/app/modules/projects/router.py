from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import require_preparation_access
from app.core.database import get_db
from app.core.project_access import ProjectAccessPolicy
from app.engines.documents.dto import GeneratedDocument
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.schemas import (
    ProjectCapabilitiesResponse,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectMemberResponse,
    ProjectOwnerTransferRequest,
    ProjectParticipantsUpdateRequest,
    ProjectRecipeGenerationModeUpdateRequest,
    ProjectResponse,
    ProjectStatusUpdateRequest,
    ProjectTeamCandidateResponse,
    ProjectTeamResponse,
    ProjectTeamUpdateRequest,
)
from app.modules.projects.service import ProjectService
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.schemas.auth import UserRole
from app.services.account_profile_service import contact_vcard
from app.services.club_settings_service import ClubSettingsService
from app.services.document_appearance_settings_service import (
    DocumentAppearanceSettingsService,
)
from app.services.equipment_list_service import EquipmentListService
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.operational_audit_service import OperationalAuditService
from app.services.project_document_package_service import ProjectDocumentPackageService
from app.services.project_document_service import ProjectDocumentService
from app.services.project_participant_recalculation_service import (
    ProjectParticipantRecalculationService,
)
from app.services.project_preparation_service import (
    ProjectPreparationResult,
    ProjectPreparationService,
)
from app.services.project_team_service import ProjectTeamService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(prefix="/projects", tags=["projects"])


def _capabilities(project: ProjectORM, actor: UserORM) -> ProjectCapabilitiesResponse:
    value = ProjectAccessPolicy.capabilities(project, actor)
    return ProjectCapabilitiesResponse(**value.__dict__)


def _project_response(project: ProjectORM, actor: UserORM) -> ProjectResponse:
    owner_display_name = project.owner.display_name if project.owner is not None else None
    if owner_display_name is None and project.owner_user_id == actor.id:
        owner_display_name = actor.display_name
    return ProjectResponse(
        id=project.id,
        name=project.name,
        participants=project.participants,
        days=project.days,
        start_date=project.start_date,
        first_meal=project.first_meal,
        last_meal=project.last_meal,
        recipe_generation_mode=RecipeGenerationMode(project.recipe_generation_mode),
        status=project.status,
        owner_user_id=project.owner_user_id,
        owner_display_name=owner_display_name,
        capabilities=_capabilities(project, actor),
    )


def _member_response(user: UserORM, project_role: str) -> ProjectMemberResponse:
    return ProjectMemberResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        telegram_url=user.telegram_url,
        max_url=user.max_url,
        vk_url=user.vk_url,
        role=UserRole(user.role),
        is_active=user.is_active,
        project_role=project_role,  # type: ignore[arg-type]
    )


def _team_response(project: ProjectORM) -> ProjectTeamResponse:
    if project.owner is None:
        raise HTTPException(status_code=409, detail="Project owner is not assigned")
    instructors = sorted(
        (link.user for link in project.instructor_links),
        key=lambda user: (user.display_name.casefold(), user.email.casefold(), user.id),
    )
    return ProjectTeamResponse(
        owner=_member_response(project.owner, "owner"),
        instructors=[
            _member_response(user, "additional_instructor") for user in instructors
        ],
    )


@router.post("", response_model=ProjectResponse)
def create_project(
    request: ProjectCreateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    try:
        created = ProjectService(ProjectRepository(db), actor=actor).create_project(
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
    project = ProjectRepository(db).get_by_id(created.id)
    if project is None:
        raise HTTPException(status_code=500, detail="Created Project could not be loaded")
    return _project_response(project, actor)


@router.get("", response_model=ProjectListResponse)
def list_projects(
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectListResponse:
    projects = ProjectRepository(db).list_visible_to(actor)
    return ProjectListResponse(
        items=[_project_response(project, actor) for project in projects]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    project = ProjectAccessPolicy.require_visible(db, project_id, actor)
    return _project_response(project, actor)


@router.get("/{project_id}/team", response_model=ProjectTeamResponse)
def get_project_team(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectTeamResponse:
    ProjectAccessPolicy.require_visible(db, project_id, actor)
    try:
        project = ProjectTeamService(db, actor=actor).get_team(project_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return _team_response(project)


@router.get(
    "/{project_id}/team/candidates",
    response_model=list[ProjectTeamCandidateResponse],
)
def list_project_team_candidates(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> list[ProjectTeamCandidateResponse]:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    candidates = ProjectTeamService(db, actor=actor).list_candidates(project_id)
    return [
        ProjectTeamCandidateResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            role=UserRole(user.role),
            is_active=user.is_active,
        )
        for user in candidates
    ]


@router.put("/{project_id}/team", response_model=ProjectTeamResponse)
def update_project_team(
    project_id: int,
    request: ProjectTeamUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectTeamResponse:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    try:
        project = ProjectTeamService(db, actor=actor).update_instructors(
            project_id,
            request.instructor_user_ids,
        )
    except (LookupError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _team_response(project)


@router.post("/{project_id}/owner-transfer", response_model=ProjectTeamResponse)
def transfer_project_ownership(
    project_id: int,
    request: ProjectOwnerTransferRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectTeamResponse:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    try:
        project = ProjectTeamService(db, actor=actor).transfer_ownership(
            project_id,
            request.new_owner_user_id,
        )
    except (LookupError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _team_response(project)


@router.get("/{project_id}/team/{user_id}/vcard")
def download_project_team_vcard(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    ProjectAccessPolicy.require_visible(db, project_id, actor)
    try:
        contact = ProjectTeamService(db, actor=actor).get_team_member(project_id, user_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if not contact.is_active:
        raise HTTPException(status_code=404, detail="Контакт команды проекта не найден.")
    return Response(
        content=contact_vcard(contact),
        media_type="text/vcard; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="tourhub-project-{project_id}-contact-{contact.id}.vcf"'
            )
        },
    )


@router.patch("/{project_id}/participants", response_model=ProjectResponse)
def update_project_participants(
    project_id: int,
    request: ProjectParticipantsUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    service = ProjectParticipantRecalculationService(
        db,
        MealPlanShoppingService(ShoppingListService(db)),
        actor=actor,
    )
    try:
        service.update_participants(project_id, request.participants)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_response(project, actor)


@router.patch("/{project_id}/recipe-generation-mode", response_model=ProjectResponse)
def update_project_recipe_generation_mode(
    project_id: int,
    request: ProjectRecipeGenerationModeUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    try:
        ProjectService(
            ProjectRepository(db),
            actor=actor,
        ).update_recipe_generation_mode(
            project_id,
            request.recipe_generation_mode.value,
        )
    except ValueError as error:
        status_code = 404 if str(error) == "Project not found" else 400
        raise HTTPException(status_code=status_code, detail=str(error)) from error
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_response(project, actor)


@router.patch("/{project_id}/status", response_model=ProjectResponse)
def complete_project(
    project_id: int,
    request: ProjectStatusUpdateRequest,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectResponse:
    ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    ProjectService(ProjectRepository(db), actor=actor).complete_project(project_id)
    project = ProjectRepository(db).get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_response(project, actor)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    ProjectAccessPolicy.require_delete(db, project_id, actor)
    ProjectService(ProjectRepository(db), actor=actor).delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{project_id}/prepare")
def prepare_project(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> ProjectPreparationResult:
    project = ProjectAccessPolicy.require_manager_write(db, project_id, actor)
    try:
        shopping_service = ShoppingListService(db)
        meal_plan_shopping_service = MealPlanShoppingService(shopping_service)
        meal_plan_repository = MealPlanRepository(db)
        preparation_service = ProjectPreparationService(
            PurchaseListService(
                PurchaseListRepository(db),
                meal_plan_repository,
                meal_plan_shopping_service,
                actor=actor,
            ),
            PurchaseChecklistService(
                PurchaseChecklistRepository(db),
                meal_plan_repository,
                meal_plan_shopping_service,
                actor=actor,
            ),
            EquipmentListService(
                EquipmentListRepository(db),
                meal_plan_repository,
                actor=actor,
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


def _record_project_document(
    *,
    db: Session,
    actor: UserORM,
    project_id: int,
    document_kind: str,
    document_format: str,
    document: GeneratedDocument,
) -> None:
    OperationalAuditService(db).record_document_generated(
        actor=actor,
        source_entity_type="project",
        source_entity_id=project_id,
        document_kind=document_kind,
        document_format=document_format,
        document=document,
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


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
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    project = ProjectAccessPolicy.require_visible(db, project_id, actor)
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
        document = generator(project)
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise
    _record_project_document(
        db=db,
        actor=actor,
        project_id=project_id,
        document_kind="purchase",
        document_format=format,
        document=document,
    )
    return _download(document)


@router.get("/{project_id}/documents/equipment/{format}")
def generate_equipment_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    project = ProjectAccessPolicy.require_visible(db, project_id, actor)
    service = _document_service(db)
    generators = {
        "pdf": service.generate_equipment_pdf,
        "excel": service.generate_equipment_excel,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")
    try:
        document = generator(project)
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise
    _record_project_document(
        db=db,
        actor=actor,
        project_id=project_id,
        document_kind="equipment",
        document_format=format,
        document=document,
    )
    return _download(document)


@router.get("/{project_id}/documents/consolidated/{format}")
def generate_consolidated_project_document(
    project_id: int,
    format: str,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    project = ProjectAccessPolicy.require_visible(db, project_id, actor)
    service = _document_service(db)
    generators = {
        "pdf": service.generate_consolidated_pdf,
        "excel": service.generate_consolidated_excel,
    }
    generator = generators.get(format)
    if generator is None:
        raise HTTPException(status_code=400, detail="Unsupported document format")
    try:
        document = generator(project)
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise
    _record_project_document(
        db=db,
        actor=actor,
        project_id=project_id,
        document_kind="consolidated",
        document_format=format,
        document=document,
    )
    return _download(document)


@router.get("/{project_id}/documents/package")
def generate_project_document_package(
    project_id: int,
    db: Session = Depends(get_db),
    actor: UserORM = Depends(require_preparation_access),
) -> Response:
    project = ProjectAccessPolicy.require_visible(db, project_id, actor)
    try:
        document = ProjectDocumentPackageService(_document_service(db)).generate_package(
            project
        )
    except ValueError as error:
        prepared_error = _prepared_document_error(error)
        if prepared_error is not None:
            raise prepared_error from error
        raise
    _record_project_document(
        db=db,
        actor=actor,
        project_id=project_id,
        document_kind="package",
        document_format="zip",
        document=document,
    )
    return _download(document)
