from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.appearance_settings import AppearanceSettingsORM
from app.schemas.appearance_settings import (
    AppearanceColorTokens,
    AppearanceHistoryResponse,
    AppearancePreset,
    AppearancePresetResponse,
    AppearanceSettingsResponse,
    AppearanceSettingsUpdateRequest,
)
from app.services.appearance_settings_service import AppearanceSettingsService
from app.services.club_settings_service import SettingsVersionConflictError

router = APIRouter(prefix="/settings/appearance", tags=["settings"])


def _response(settings: AppearanceSettingsORM) -> AppearanceSettingsResponse:
    return AppearanceSettingsResponse(
        version=settings.version,
        preset_name=AppearancePreset(settings.preset_name),
        font_family=settings.font_family,
        density=settings.density,
        border_radius=settings.border_radius,
        button_style=settings.button_style,
        card_style=settings.card_style,
        shadows_enabled=settings.shadows_enabled,
        light=AppearanceColorTokens(**settings.light_tokens),
        dark=AppearanceColorTokens(**settings.dark_tokens),
        updated_at=settings.updated_at,
    )


@router.get("", response_model=AppearanceSettingsResponse)
def get_appearance_settings(
    db: Session = Depends(get_db),
) -> AppearanceSettingsResponse:
    return _response(AppearanceSettingsService(db).get())


@router.put("", response_model=AppearanceSettingsResponse)
def update_appearance_settings(
    request: AppearanceSettingsUpdateRequest,
    db: Session = Depends(get_db),
) -> AppearanceSettingsResponse:
    service = AppearanceSettingsService(db)
    try:
        settings = service.update(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _response(settings)


@router.get("/presets", response_model=list[AppearancePresetResponse])
def get_appearance_presets() -> list[AppearancePresetResponse]:
    return AppearanceSettingsService.presets()


@router.get("/history", response_model=list[AppearanceHistoryResponse])
def get_appearance_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[AppearanceHistoryResponse]:
    return [
        AppearanceHistoryResponse(
            id=item.id,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in AppearanceSettingsService(db).list_history(limit=limit)
    ]
