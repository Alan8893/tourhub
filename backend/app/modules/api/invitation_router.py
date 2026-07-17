from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
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
from app.services.invitation_service import (
    InvitationConflictError,
    InvitationNotFoundError,
    InvitationPolicyError,
    InvitationService,
    InvitationStateError,
)

router = APIRouter(prefix="/invitations", tags=["invitations"])


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
) -> InvitationCreatedResponse:
    item = _item_response(invitation)
    return InvitationCreatedResponse(
        **item.model_dump(),
        token=raw_token,
        acceptance_path=f"/accept-invitation?token={raw_token}",
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
    return _created_response(invitation, raw_token)


@router.post("/{invitation_id}/reissue", response_model=InvitationCreatedResponse)
def reissue_invitation(
    invitation_id: int,
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
    return _created_response(invitation, raw_token)


@router.post("/{invitation_id}/revoke", response_model=InvitationListItemResponse)
def revoke_invitation(
    invitation_id: int,
    _: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> InvitationListItemResponse:
    try:
        invitation = InvitationService(db).revoke(invitation_id)
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
