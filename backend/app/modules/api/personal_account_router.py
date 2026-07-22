from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.account_profile import (
    AccountProfileResponse,
    AccountProfileUpdateRequest,
    AccountSessionResponse,
    PasswordChangeRequest,
)
from app.schemas.auth import UserRole
from app.services.account_profile_service import (
    AccountProfileService,
    AccountVersionConflictError,
    CurrentSessionNotFoundError,
    InvalidCurrentPasswordError,
)
from app.services.session_administration_service import (
    AccountSessionNotFoundError,
    AccountSessionView,
    CurrentSessionRevocationError,
    SessionAdministrationService,
    SessionContextNotFoundError,
)

router = APIRouter(prefix="/account", tags=["account"])


def _profile_response(user: UserORM) -> AccountProfileResponse:
    return AccountProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        telegram_url=user.telegram_url,
        max_url=user.max_url,
        vk_url=user.vk_url,
        role=UserRole(user.role),
        is_active=user.is_active,
        version=user.version,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _session_response(item: AccountSessionView) -> AccountSessionResponse:
    return AccountSessionResponse(
        id=item.id,
        created_at=item.created_at,
        last_seen_at=item.last_seen_at,
        expires_at=item.expires_at,
        is_current=item.is_current,
    )


def _current_raw_token(request: Request) -> str:
    raw_token = request.cookies.get(settings.auth.session_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Текущая сессия больше не активна.")
    return raw_token


@router.get("", response_model=AccountProfileResponse)
def get_profile(user: UserORM = Depends(get_current_user)) -> AccountProfileResponse:
    return _profile_response(user)


@router.patch("", response_model=AccountProfileResponse)
def update_profile(
    request: AccountProfileUpdateRequest,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountProfileResponse:
    try:
        updated = AccountProfileService(db, actor=user).update_profile(request)
    except AccountVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except CurrentSessionNotFoundError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return _profile_response(updated)


@router.post("/password", response_model=AccountProfileResponse)
def change_password(
    payload: PasswordChangeRequest,
    request: Request,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AccountProfileResponse:
    try:
        updated = AccountProfileService(db, actor=user).change_password(
            payload,
            current_raw_token=_current_raw_token(request),
        )
    except InvalidCurrentPasswordError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except CurrentSessionNotFoundError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return _profile_response(updated)


@router.get("/sessions", response_model=list[AccountSessionResponse])
def list_sessions(
    request: Request,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AccountSessionResponse]:
    try:
        sessions = SessionAdministrationService(db, actor=user).list_active(
            current_raw_token=_current_raw_token(request)
        )
    except SessionContextNotFoundError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return [_session_response(item) for item in sessions]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(
    session_id: int,
    request: Request,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    try:
        SessionAdministrationService(db, actor=user).revoke(
            session_id,
            current_raw_token=_current_raw_token(request),
        )
    except SessionContextNotFoundError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except AccountSessionNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except CurrentSessionRevocationError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
