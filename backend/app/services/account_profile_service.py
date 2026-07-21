from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.schemas.account_profile import AccountProfileUpdateRequest, PasswordChangeRequest
from app.services.audit_service import AuditService
from app.services.auth_service import hash_password, token_hash, utc_now, verify_password


class AccountVersionConflictError(RuntimeError):
    pass


class InvalidCurrentPasswordError(RuntimeError):
    pass


class CurrentSessionNotFoundError(RuntimeError):
    pass


class ContactNotFoundError(RuntimeError):
    pass


class AccountProfileService:
    def __init__(self, session: Session, *, actor: UserORM) -> None:
        self.session = session
        self.actor = actor

    def update_profile(self, request: AccountProfileUpdateRequest) -> UserORM:
        try:
            user = self._locked_actor()
            if user.version != request.version:
                raise AccountVersionConflictError(
                    "Профиль уже изменён в другой вкладке. Обновите страницу и повторите."
                )

            editable_fields = (
                "display_name",
                "phone",
                "telegram_url",
                "max_url",
                "vk_url",
            )
            changed_fields = [
                field
                for field in editable_fields
                if getattr(user, field) != getattr(request, field)
            ]
            if not changed_fields:
                return user

            previous_version = user.version
            for field in changed_fields:
                setattr(user, field, getattr(request, field))
            user.version += 1

            AuditService(self.session).record(
                actor=user,
                action="account_profile_updated",
                entity_type="user",
                entity_id=user.id,
                before={"version": previous_version},
                after={"version": user.version},
                context={"changed_fields": changed_fields},
            )
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def change_password(
        self,
        request: PasswordChangeRequest,
        *,
        current_raw_token: str,
    ) -> UserORM:
        try:
            user = self._locked_actor()
            if not verify_password(request.current_password, user.password_hash):
                raise InvalidCurrentPasswordError("Текущий пароль указан неверно.")

            current_token_hash = token_hash(current_raw_token)
            current_session = self.session.scalar(
                select(AuthSessionORM).where(
                    AuthSessionORM.user_id == user.id,
                    AuthSessionORM.token_hash == current_token_hash,
                    AuthSessionORM.revoked_at.is_(None),
                )
            )
            if current_session is None:
                raise CurrentSessionNotFoundError("Текущая сессия больше не активна.")

            previous_version = user.version
            user.password_hash = hash_password(request.new_password)
            user.version += 1
            revoked_at = utc_now()
            result = self.session.execute(
                update(AuthSessionORM)
                .where(
                    AuthSessionORM.user_id == user.id,
                    AuthSessionORM.token_hash != current_token_hash,
                    AuthSessionORM.revoked_at.is_(None),
                )
                .values(revoked_at=revoked_at)
            )
            revoked_count = int(result.rowcount or 0)

            AuditService(self.session).record(
                actor=user,
                action="account_password_changed",
                entity_type="user",
                entity_id=user.id,
                before={"version": previous_version},
                after={"version": user.version},
                context={
                    "current_session_preserved": True,
                    "revoked_other_session_count": revoked_count,
                },
            )
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def list_contacts(self) -> list[UserORM]:
        return list(
            self.session.scalars(
                select(UserORM)
                .where(UserORM.is_active.is_(True))
                .order_by(UserORM.display_name, UserORM.email, UserORM.id)
            ).all()
        )

    def get_contact(self, user_id: int) -> UserORM:
        user = self.session.scalar(
            select(UserORM).where(UserORM.id == user_id, UserORM.is_active.is_(True))
        )
        if user is None:
            raise ContactNotFoundError("Контакт участника не найден.")
        return user

    def _locked_actor(self) -> UserORM:
        user = self.session.scalar(
            select(UserORM).where(UserORM.id == self.actor.id).with_for_update()
        )
        if user is None or not user.is_active:
            raise CurrentSessionNotFoundError("Текущий пользователь больше не активен.")
        return user


def contact_vcard(user: UserORM) -> str:
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{_vcard_escape(user.display_name)}",
        f"EMAIL;TYPE=INTERNET:{_vcard_escape(user.email)}",
    ]
    if user.phone:
        lines.append(f"TEL;TYPE=CELL:{_vcard_escape(user.phone)}")
    for label, url in (
        ("Telegram", user.telegram_url),
        ("MAX", user.max_url),
        ("VK", user.vk_url),
    ):
        if url:
            lines.append(f"URL;TYPE={label}:{_vcard_escape(url)}")
    lines.extend(("END:VCARD", ""))
    return "\r\n".join(lines)


def _vcard_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\r", "")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )
