from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.club_settings import (
    ClubSettingsResponse,
    ClubSettingsUpdateRequest,
)
from app.services.club_settings_service import ClubSettingsService
from app.services.settings_audit_service import SettingsAuditService

router = APIRouter(prefix="/club-settings", tags=["club-settings"])


def _response(service: ClubSettingsService) -> ClubSettingsResponse:
    settings = service.get()
    return ClubSettingsResponse(
        club_name=settings.club_name,
        logo_data_url=service.logo_data_url(settings),
    )


@router.get("", response_model=ClubSettingsResponse)
def get_club_settings(db: Session = Depends(get_db)) -> ClubSettingsResponse:
    return _response(ClubSettingsService(db))


@router.put("", response_model=ClubSettingsResponse)
def update_club_settings(
    request: ClubSettingsUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> ClubSettingsResponse:
    service = ClubSettingsService(db)
    try:
        current = service.get()
        plan = SettingsAuditService.plan_legacy_club_update(
            service,
            current,
            **request.model_dump(),
        )
        SettingsAuditService(db, administrator).stage(plan)
        service.update(**request.model_dump())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return _response(service)
