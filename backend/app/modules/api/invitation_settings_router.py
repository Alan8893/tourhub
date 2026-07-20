from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.invitation_settings import InvitationSettingsORM
from app.models.user import UserORM
from app.schemas.invitation_settings import (
    InvitationDefaultRole,
    InvitationSettingsHistoryResponse,
    InvitationSettingsResponse,
    InvitationSettingsUpdateRequest,
)
from app.services.club_settings_service import SettingsVersionConflictError
from app.services.invitation_settings_service import InvitationSettingsService
from app.services.settings_audit_service import SettingsAuditService

router = APIRouter(prefix="/settings/invitations", tags=["settings"])


def _response(settings: InvitationSettingsORM) -> InvitationSettingsResponse:
    return InvitationSettingsResponse(
        version=settings.version,
        expires_after_days=settings.expires_after_days,
        default_role=InvitationDefaultRole(settings.default_role),
        allowed_email_domains=settings.allowed_email_domains,
        allow_resend=settings.allow_resend,
        active_invitation_limit=settings.active_invitation_limit,
        administrators_only=settings.administrators_only,
        require_email_confirmation=settings.require_email_confirmation,
        updated_at=settings.updated_at,
    )


@router.get("", response_model=InvitationSettingsResponse)
def get_invitation_settings(
    db: Session = Depends(get_db),
) -> InvitationSettingsResponse:
    return _response(InvitationSettingsService(db).get())


@router.put("", response_model=InvitationSettingsResponse)
def update_invitation_settings(
    request: InvitationSettingsUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> InvitationSettingsResponse:
    service = InvitationSettingsService(db)
    try:
        current = service.get()
        plan = SettingsAuditService.plan_invitation_update(current, request)
        SettingsAuditService(db, administrator).stage(plan)
        settings = service.update(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(settings)


@router.get("/history", response_model=list[InvitationSettingsHistoryResponse])
def get_invitation_settings_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[InvitationSettingsHistoryResponse]:
    return [
        InvitationSettingsHistoryResponse(
            id=item.id,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in InvitationSettingsService(db).list_history(limit=limit)
    ]
