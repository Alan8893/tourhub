from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.schemas.auth import UserRole
from app.schemas.user_administration import UserAdministrationUpdateRequest
from app.services.auth_service import utc_now


class UserAdministrationError(RuntimeError):
    pass


class UserNotFoundError(UserAdministrationError):
    pass


class UserVersionConflictError(UserAdministrationError):
    pass


class LastActiveAdministratorError(UserAdministrationError):
    pass


class UserAdministrationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> Sequence[UserORM]:
        return self.session.scalars(
            select(UserORM).order_by(UserORM.display_name, UserORM.email, UserORM.id)
        ).all()

    def update(
        self,
        user_id: int,
        request: UserAdministrationUpdateRequest,
    ) -> UserORM:
        users = self.session.scalars(
            select(UserORM).order_by(UserORM.id).with_for_update()
        ).all()
        user = next((item for item in users if item.id == user_id), None)
        if user is None:
            raise UserNotFoundError("Пользователь не найден.")
        if user.version != request.expected_version:
            raise UserVersionConflictError(
                "Данные пользователя изменились в другом окне. Перезагрузите список."
            )

        removes_active_administrator = (
            user.role == UserRole.ADMINISTRATOR.value
            and user.is_active
            and (
                request.role is not UserRole.ADMINISTRATOR
                or not request.is_active
            )
        )
        if removes_active_administrator:
            active_administrators = sum(
                1
                for item in users
                if item.role == UserRole.ADMINISTRATOR.value and item.is_active
            )
            if active_administrators <= 1:
                raise LastActiveAdministratorError(
                    "Нельзя отключить или понизить последнего активного администратора."
                )

        role_changed = user.role != request.role.value
        active_changed = user.is_active != request.is_active
        if not role_changed and not active_changed:
            return user

        was_active = user.is_active
        user.role = request.role.value
        user.is_active = request.is_active
        user.version += 1

        if was_active and not request.is_active:
            self.session.execute(
                update(AuthSessionORM)
                .where(
                    AuthSessionORM.user_id == user.id,
                    AuthSessionORM.revoked_at.is_(None),
                )
                .values(revoked_at=utc_now())
            )

        self.session.commit()
        self.session.refresh(user)
        return user
