from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.document_appearance_settings import DocumentAppearanceSettingsORM
from app.models.user import UserORM
from app.schemas.document_appearance_settings import (
    DocumentAppearanceHistoryResponse,
    DocumentAppearanceSettingsResponse,
    DocumentAppearanceSettingsUpdateRequest,
    DocumentLogoSource,
    DocumentTableDensity,
)
from app.services.club_settings_service import SettingsVersionConflictError
from app.services.document_appearance_settings_service import (
    DocumentAppearanceSettingsService,
)
from app.services.settings_audit_service import SettingsAuditService

router = APIRouter(prefix="/settings/documents", tags=["settings"])


def _response(
    settings: DocumentAppearanceSettingsORM,
) -> DocumentAppearanceSettingsResponse:
    return DocumentAppearanceSettingsResponse(
        version=settings.version,
        primary_color=settings.primary_color,
        accent_color=settings.accent_color,
        heading_color=settings.heading_color,
        table_header_background=settings.table_header_background,
        table_header_text=settings.table_header_text,
        table_border_color=settings.table_border_color,
        title_background_color=settings.title_background_color,
        logo_source=DocumentLogoSource(settings.logo_source),
        show_contacts=settings.show_contacts,
        footer_text=settings.footer_text,
        use_document_image_as_title_background=(
            settings.use_document_image_as_title_background
        ),
        table_density=DocumentTableDensity(settings.table_density),
        updated_at=settings.updated_at,
    )


@router.get("", response_model=DocumentAppearanceSettingsResponse)
def get_document_appearance_settings(
    db: Session = Depends(get_db),
) -> DocumentAppearanceSettingsResponse:
    return _response(DocumentAppearanceSettingsService(db).get())


@router.put("", response_model=DocumentAppearanceSettingsResponse)
def update_document_appearance_settings(
    request: DocumentAppearanceSettingsUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> DocumentAppearanceSettingsResponse:
    service = DocumentAppearanceSettingsService(db)
    try:
        current = service.get()
        plan = SettingsAuditService.plan_document_update(current, request)
        SettingsAuditService(db, administrator).stage(plan)
        settings = service.update(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _response(settings)


@router.get("/history", response_model=list[DocumentAppearanceHistoryResponse])
def get_document_appearance_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[DocumentAppearanceHistoryResponse]:
    return [
        DocumentAppearanceHistoryResponse(
            id=item.id,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in DocumentAppearanceSettingsService(db).list_history(limit=limit)
    ]
