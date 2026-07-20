from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.module_settings import ModuleSettingsORM
from app.models.user import UserORM
from app.schemas.module_settings import (
    ModuleSettingsHistoryResponse,
    ModuleSettingsResponse,
    ModuleSettingsUpdateRequest,
)
from app.services.club_settings_service import SettingsVersionConflictError
from app.services.module_settings_service import ModuleSettingsService
from app.services.settings_audit_service import SettingsAuditService

router = APIRouter(prefix="/settings/modules", tags=["settings"])


def _response(
    service: ModuleSettingsService,
    settings: ModuleSettingsORM,
) -> ModuleSettingsResponse:
    return ModuleSettingsResponse(
        version=settings.version,
        projects_visible=settings.projects_visible,
        catalogue_visible=settings.catalogue_visible,
        catalog_import_visible=settings.catalog_import_visible,
        shopping_visible=settings.shopping_visible,
        equipment_visible=settings.equipment_visible,
        documents_visible=settings.documents_visible,
        modules=service.definitions(settings),
        updated_at=settings.updated_at,
    )


@router.get("", response_model=ModuleSettingsResponse)
def get_module_settings(
    db: Session = Depends(get_db),
) -> ModuleSettingsResponse:
    service = ModuleSettingsService(db)
    return _response(service, service.get())


@router.put("", response_model=ModuleSettingsResponse)
def update_module_settings(
    request: ModuleSettingsUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> ModuleSettingsResponse:
    service = ModuleSettingsService(db)
    try:
        current = service.get()
        plan = SettingsAuditService.plan_module_update(current, request)
        SettingsAuditService(db, administrator).stage(plan)
        settings = service.update(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _response(service, settings)


@router.get("/history", response_model=list[ModuleSettingsHistoryResponse])
def get_module_settings_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[ModuleSettingsHistoryResponse]:
    return [
        ModuleSettingsHistoryResponse(
            id=item.id,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in ModuleSettingsService(db).list_history(limit=limit)
    ]
