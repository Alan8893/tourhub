from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserORM
from app.schemas.auth import UserRole
from app.services.auth_service import AuthService


def get_current_user(
    session_token: str | None = Cookie(
        default=None,
        alias=settings.auth.session_cookie_name,
    ),
    db: Session = Depends(get_db),
) -> UserORM:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется вход в TourHub.",
        )
    user = AuthService(db).resolve_user(session_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Сессия недействительна или истекла.",
        )
    return user


def require_administrator(user: UserORM = Depends(get_current_user)) -> UserORM:
    if user.role != UserRole.ADMINISTRATOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ разрешён только администратору.",
        )
    return user
