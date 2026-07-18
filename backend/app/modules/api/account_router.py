from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_administrator
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.auth import UserRole
from app.schemas.user_administration import (
    UserAdministrationResponse,
    UserAdministrationUpdateRequest,
)
from app.services.user_administration_service import (
    LastActiveAdministratorError,
    UserAdministrationService,
    UserNotFoundError,
    UserVersionConflictError,
)

router = APIRouter(prefix="/users", tags=["users"])


def _response(user: UserORM, *, current_user_id: int) -> UserAdministrationResponse:
    return UserAdministrationResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=UserRole(user.role),
        is_active=user.is_active,
        version=user.version,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        is_current=user.id == current_user_id,
    )


@router.get("", response_model=list[UserAdministrationResponse])
def list_users(
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> list[UserAdministrationResponse]:
    return [
        _response(user, current_user_id=administrator.id)
        for user in UserAdministrationService(db).list()
    ]


@router.patch("/{user_id}", response_model=UserAdministrationResponse)
def update_user(
    user_id: int,
    request: UserAdministrationUpdateRequest,
    administrator: UserORM = Depends(require_administrator),
    db: Session = Depends(get_db),
) -> UserAdministrationResponse:
    try:
        user = UserAdministrationService(db).update(user_id, request)
    except UserNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except UserVersionConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except LastActiveAdministratorError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return _response(user, current_user_id=administrator.id)
