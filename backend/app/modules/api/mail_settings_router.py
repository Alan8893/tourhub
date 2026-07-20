from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.mail_settings import MailSettingsORM
from app.models.user import UserORM
from app.schemas.mail_settings import (
    MailOperationResponse,
    MailSecurityMode,
    MailSettingsHistoryResponse,
    MailSettingsResponse,
    MailSettingsUpdateRequest,
)
from app.services.club_settings_service import SettingsVersionConflictError
from app.services.mail_delivery_service import (
    MailDeliveryFailedError,
    MailDeliveryService,
    MailDeliveryUnavailableError,
)
from app.services.mail_settings_service import MAIL_SECRET_ENV_VAR, MailSettingsService
from app.services.settings_audit_service import SettingsAuditService

router = APIRouter(prefix="/settings/mail", tags=["settings"])


def _response(
    settings: MailSettingsORM,
    service: MailSettingsService,
) -> MailSettingsResponse:
    return MailSettingsResponse(
        version=settings.version,
        smtp_host=settings.smtp_host,
        smtp_port=settings.smtp_port,
        security_mode=MailSecurityMode(settings.security_mode),
        smtp_username=settings.smtp_username,
        sender_email=settings.sender_email,
        sender_name=settings.sender_name,
        reply_to_email=settings.reply_to_email,
        test_recipient_email=settings.test_recipient_email,
        timeout_seconds=settings.timeout_seconds,
        retry_count=settings.retry_count,
        updated_at=settings.updated_at,
        secret_configured=service.secret_configured(),
        secret_source="environment",
        secret_environment_variable=MAIL_SECRET_ENV_VAR,
        delivery_available=MailDeliveryService.configuration_available(settings),
        test_delivery_available=MailDeliveryService.test_delivery_available(settings),
    )


def _operation_error(error: RuntimeError) -> HTTPException:
    if isinstance(error, MailDeliveryUnavailableError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, MailDeliveryFailedError):
        return HTTPException(status_code=502, detail=str(error))
    return HTTPException(status_code=500, detail="Не удалось выполнить почтовую операцию.")


def _record_operation_failure(
    *,
    db: Session,
    administrator: UserORM,
    settings: MailSettingsORM,
    action: str,
    error: RuntimeError,
) -> None:
    if isinstance(error, MailDeliveryUnavailableError):
        status = "unavailable"
        attempts = 0
    elif isinstance(error, MailDeliveryFailedError):
        status = "failed"
        attempts = error.attempts
    else:
        status = "failed"
        attempts = 0
    SettingsAuditService(db, administrator).record_mail_operation(
        action=action,
        settings=settings,
        status=status,
        attempts=attempts,
    )


@router.get("", response_model=MailSettingsResponse)
def get_mail_settings(
    db: Session = Depends(get_db),
) -> MailSettingsResponse:
    service = MailSettingsService(db)
    return _response(service.get(), service)


@router.put("", response_model=MailSettingsResponse)
def update_mail_settings(
    request: MailSettingsUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> MailSettingsResponse:
    service = MailSettingsService(db)
    try:
        current = service.get()
        plan = SettingsAuditService.plan_mail_update(current, request)
        SettingsAuditService(db, administrator).stage(plan)
        settings = service.update(request)
    except SettingsVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(settings, service)


@router.post("/check", response_model=MailOperationResponse)
def check_mail_connection(
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> MailOperationResponse:
    settings = MailSettingsService(db).get()
    try:
        result = MailDeliveryService(db).check_connection()
    except RuntimeError as error:
        _record_operation_failure(
            db=db,
            administrator=administrator,
            settings=settings,
            action="mail_connection_checked",
            error=error,
        )
        raise _operation_error(error) from error
    SettingsAuditService(db, administrator).record_mail_operation(
        action="mail_connection_checked",
        settings=settings,
        status=result.status.value,
        attempts=result.attempts,
        recipient=result.recipient,
    )
    return MailOperationResponse(
        status=result.status,
        message=result.message,
        attempts=result.attempts,
        recipient=result.recipient,
    )


@router.post("/test", response_model=MailOperationResponse)
def send_test_mail(
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> MailOperationResponse:
    settings = MailSettingsService(db).get()
    try:
        result = MailDeliveryService(db).send_test_message()
    except RuntimeError as error:
        _record_operation_failure(
            db=db,
            administrator=administrator,
            settings=settings,
            action="mail_test_message_delivery",
            error=error,
        )
        raise _operation_error(error) from error
    SettingsAuditService(db, administrator).record_mail_operation(
        action="mail_test_message_delivery",
        settings=settings,
        status=result.status.value,
        attempts=result.attempts,
        recipient=result.recipient,
    )
    return MailOperationResponse(
        status=result.status,
        message=result.message,
        attempts=result.attempts,
        recipient=result.recipient,
    )


@router.get("/history", response_model=list[MailSettingsHistoryResponse])
def get_mail_settings_history(
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[MailSettingsHistoryResponse]:
    return [
        MailSettingsHistoryResponse(
            id=item.id,
            actor_label=item.actor_label,
            action=item.action,
            changed_fields=item.changed_fields,
            settings_version=item.settings_version,
            created_at=item.created_at,
        )
        for item in MailSettingsService(db).list_history(limit=limit)
    ]
