import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.config import settings
from app.core.database import get_db
from app.models.invitation import InvitationORM
from app.models.user import UserORM
from app.schemas.auth import AuthResponse, UserResponse, UserRole
from app.schemas.invitation import (
    InvitationAcceptRequest,
    InvitationCreateRequest,
    InvitationCreatedResponse,
    InvitationDefaultRole,
    InvitationListItemResponse,
    InvitationPublicResponse,
    InvitationTokenRequest,
)
from app.services.invitation_audit_service import InvitationAuditService
from app.services.invitation_service import (
    InvitationConflictError,
    InvitationNotFoundError,
    InvitationPolicyError,
    InvitationService,
    InvitationStateError,
)
from app.services.mail_delivery_service import MailDeliveryResult, MailDeliveryService

router = APIRouter(prefix="/invitations", tags=["invitations"])
logger = logging.getLogger(__name__)


def _item_response(invitation: InvitationORM) -> InvitationListItemResponse:
    return InvitationListItemResponse(
        id=invitation.id,
        email=invitation.email,
        role=InvitationDefaultRole(invitation.role),
        status=InvitationService.status_of(invitation),
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        consumed_at=invitation.consumed_at,
        revoked_at=invitation.revoked_at,
        superseded_at=invitation.superseded_at,
    )


def _created_response(
    invitation: InvitationORM,
    raw_token: str,
    delivery: MailDeliveryResult,
) -> InvitationCreatedResponse:
    item = _item_response(invitation)
    return InvitationCreatedResponse(
        **item.model_dump(),
        token=raw_token,
        acceptance_path=f"/accept-invitation#token={raw_token}",
        delivery_status=delivery.status,
        delivery_message=delivery.message,
        delivery_attempts=delivery.attempts,
    )


def _user_response(user: UserORM) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=UserRole(user.role),
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _set_session_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=settings.auth.session_cookie_name,
        value=raw_token,
        max_age=settings.auth.session_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth.cookie_secure,
        samesite="lax",
        path="/",
    )


def _translate_error(error: RuntimeError) -> HTTPException:
    if isinstance(error, InvitationNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    if isinstance(error, InvitationStateError):
        return HTTPException(status_code=410, detail=str(error))
    if isinstance(error, InvitationConflictError):
        return HTTPException(status_code=409, detail=str(error))
    if isinstance(error, InvitationPolicyError):
        return HTTPException(status_code=422, detail=str(error))
    return HTTPException(status_code=500, detail="Не удалось обработать приглашение.")


def _role_label(role: str) -> str:
    if role == InvitationDefaultRole.VERIFIED_INSTRUCTOR.value:
        return "Проверенный инструктор"
    return "Инструктор"


def _deliver(
    invitation: InvitationORM,
    raw_token: str,
    *,
    http_request: Request,
    db: Session,
) -> MailDeliveryResult:
    acceptance_path = f"/accept-invitation#token={raw_token}"
    acceptance_url = f"{str(http_request.base_url).rstrip('/')}{acceptance_path}"
    return MailDeliveryService(db).send_invitation_best_effort(
        recipient=invitation.email,
        role_label=_role_label(invitation.role),
        expires_at=invitation.expires_at,
        acceptance_url=acceptance_url,
    )


def _record_delivery_result(
    *,
    db: Session,
    administrator: UserORM,
    invitation: InvitationORM,
    operation: Literal["create", "reissue"],
    delivery: MailDeliveryResult,
) -> None:
    try:
        InvitationAuditService(db).record_delivery_result(
            actor=administrator,
            invitation=invitation,
            operation=operation,
            result=delivery,
        )
    except Exception:
        db.rollback()
        logger.exception(
            "Invitation delivery audit write failed",
            extra={
                "invitation_id": invitation.id,
                "operation": operation,
            },
        )


@router.get("", response_model=list[InvitationListItemResponse])
def list_invitations(
    limit: int = Query(default=100, ge=1, le=200),
    _: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> list[InvitationListItemResponse]:
    return [
        _item_response(item)
        for item in InvitationService(db).list(limit=limit)
    ]


@router.post(
    "",
    response_model=InvitationCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    request: InvitationCreateRequest,
    http_request: Request,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> InvitationCreatedResponse:
    try:
        invitation, raw_token = InvitationService(db).create(
            request,
            actor=administrator,
        )
    except RuntimeError as error:
        raise _translate_error(error) from error
    delivery = _deliver(invitation, raw_token, http_request=http_request, db=db)
    _record_delivery_result(
        db=db,
        administrator=administrator,
        invitation=invitation,
        operation="create",
        delivery=delivery,
    )
    return _created_response(invitation, raw_token, delivery)


@router.post("/{invitation_id}/reissue", response_model=InvitationCreatedResponse)
def reissue_invitation(
    invitation_id: int,
    http_request: Request,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> InvitationCreatedResponse:
    try:
        invitation, raw_token = InvitationService(db).reissue(
            invitation_id,
            actor=administrator,
        )
    except RuntimeError as error:
        raise _translate_error(error) from error
    delivery = _deliver(invitation, raw_token, http_request=http_request, db=db)
    _record_delivery_result(
        db=db,
        administrator=administrator,
        invitation=invitation,
        operation="reissue",
        delivery=delivery,
    )
    return _created_response(invitation, raw_token, delivery)


@router.post("/{invitation_id}/revoke", response_model=InvitationListItemResponse)
def revoke_invitation(
    invitation_id: int,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> InvitationListItemResponse:
    try:
        invitation = InvitationService(db).revoke(
            invitation_id,
            actor=administrator,
        )
    except RuntimeError as error:
        raise _translate_error(error) from error
    return _item_response(invitation)


@router.post("/inspect", response_model=InvitationPublicResponse)
def inspect_invitation(
    request: InvitationTokenRequest,
    db: Session = Depends(get_db),
) -> InvitationPublicResponse:
    try:
        invitation = InvitationService(db).inspect(request.token)
    except RuntimeError as error:
        raise _translate_error(error) from error
    return InvitationPublicResponse(
        email=invitation.email,
        role=InvitationDefaultRole(invitation.role),
        expires_at=invitation.expires_at,
    )


@router.post("/accept", response_model=AuthResponse)
def accept_invitation(
    request: InvitationAcceptRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    try:
        user, raw_session = InvitationService(db).accept(request)
    except RuntimeError as error:
        raise _translate_error(error) from error
    _set_session_cookie(response, raw_session)
    return AuthResponse(user=_user_response(user))
