from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.account_profile import (
    AccountProfileResponse,
    AccountProfileUpdateRequest,
    ClubContactResponse,
    PasswordChangeRequest,
)
from app.schemas.auth import UserRole
from app.services.account_profile_service import (
    AccountProfileService,
    AccountVersionConflictError,
    ContactNotFoundError,
    CurrentSessionNotFoundError,
    InvalidCurrentPasswordError,
    contact_vcard,
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


def _contact_response(user: UserORM, *, current_user_id: int) -> ClubContactResponse:
    return ClubContactResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        phone=user.phone,
        telegram_url=user.telegram_url,
        max_url=user.max_url,
        vk_url=user.vk_url,
        role=UserRole(user.role),
        is_current=user.id == current_user_id,
    )


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
    current_raw_token = request.cookies.get(settings.auth.session_cookie_name)
    if not current_raw_token:
        raise HTTPException(status_code=401, detail="Текущая сессия больше не активна.")
    try:
        updated = AccountProfileService(db, actor=user).change_password(
            payload,
            current_raw_token=current_raw_token,
        )
    except InvalidCurrentPasswordError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except CurrentSessionNotFoundError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    return _profile_response(updated)


@router.get("/contacts", response_model=list[ClubContactResponse])
def list_contacts(
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClubContactResponse]:
    contacts = AccountProfileService(db, actor=user).list_contacts()
    return [_contact_response(contact, current_user_id=user.id) for contact in contacts]


@router.get("/contacts/{user_id}/vcard")
def download_contact_vcard(
    user_id: int,
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    try:
        contact = AccountProfileService(db, actor=user).get_contact(user_id)
    except ContactNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Response(
        content=contact_vcard(contact),
        media_type="text/vcard; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="tourhub-contact-{contact.id}.vcf"'
            )
        },
    )
