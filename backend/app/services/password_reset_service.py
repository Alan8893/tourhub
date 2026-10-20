from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_session import AuthSessionORM
from app.models.password_reset import PasswordResetAttemptORM, PasswordResetTokenORM
from app.models.user import UserORM
from app.schemas.password_reset import PasswordResetRequest
from app.services.auth_service import hash_password, token_hash, utc_now
from app.services.mail_delivery_service import MailDeliveryService

TOKEN_TTL_MINUTES = 30
EMAIL_LIMIT = 3
EMAIL_WINDOW_MINUTES = 15
IP_LIMIT = 10
IP_WINDOW_MINUTES = 60
GENERIC_REQUEST_MESSAGE = (
    "Если учётная запись с таким email существует, инструкция по восстановлению будет отправлена."
)


class InvalidPasswordResetTokenError(RuntimeError):
    pass


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class PasswordResetService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def request_reset(self, request: PasswordResetRequest, *, client_ip: str) -> None:
        now = utc_now()
        email_hash = _digest(request.email)
        ip_hash = _digest(client_ip or "unknown")
        try:
            self.session.execute(
                delete(PasswordResetAttemptORM).where(
                    PasswordResetAttemptORM.requested_at < now - timedelta(days=1)
                )
            )
            email_count = self.session.scalar(
                select(PasswordResetAttemptORM.id)
                .where(
                    PasswordResetAttemptORM.email_hash == email_hash,
                    PasswordResetAttemptORM.requested_at
                    >= now - timedelta(minutes=EMAIL_WINDOW_MINUTES),
                )
                .limit(EMAIL_LIMIT)
            )
            email_count_reached = email_count is not None
            ip_count = self.session.scalar(
                select(PasswordResetAttemptORM.id)
                .where(
                    PasswordResetAttemptORM.ip_hash == ip_hash,
                    PasswordResetAttemptORM.requested_at >= now - timedelta(hours=IP_WINDOW_MINUTES // 60),
                )
                .offset(IP_LIMIT - 1)
                .limit(1)
            )
            throttled = email_count_reached or ip_count is not None
            self.session.add(
                PasswordResetAttemptORM(
                    email_hash=email_hash,
                    ip_hash=ip_hash,
                    requested_at=now,
                )
            )
            user = self.session.scalar(
                select(UserORM).where(UserORM.email == request.email, UserORM.is_active.is_(True))
            )
            raw_token: str | None = None
            if user is not None and not throttled:
                self.session.execute(
                    update(PasswordResetTokenORM)
                    .where(
                        PasswordResetTokenORM.user_id == user.id,
                        PasswordResetTokenORM.consumed_at.is_(None),
                    )
                    .values(consumed_at=now)
                )
                raw_token = secrets.token_urlsafe(32)
                self.session.add(
                    PasswordResetTokenORM(
                        user_id=user.id,
                        token_hash=token_hash(raw_token),
                        expires_at=now + timedelta(minutes=TOKEN_TTL_MINUTES),
                    )
                )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        if user is None or throttled or raw_token is None:
            return

        base_url = settings.frontend_public_url.rstrip("/")
        reset_url = f"{base_url}/reset-password#token={raw_token}"
        try:
            MailDeliveryService(self.session).send_password_reset_best_effort(
                recipient=user.email,
                reset_url=reset_url,
                expires_in_minutes=TOKEN_TTL_MINUTES,
            )
        except Exception:
            # The public endpoint deliberately does not expose delivery outcomes.
            return

    def confirm_reset(self, *, raw_token: str, password: str) -> None:
        now = utc_now()
        try:
            token = self.session.scalar(
                select(PasswordResetTokenORM)
                .where(PasswordResetTokenORM.token_hash == token_hash(raw_token))
                .with_for_update()
            )
            if (
                token is None
                or token.consumed_at is not None
                or token.expires_at <= now
            ):
                raise InvalidPasswordResetTokenError("Ссылка восстановления недействительна или устарела.")
            user = self.session.scalar(
                select(UserORM).where(UserORM.id == token.user_id).with_for_update()
            )
            if user is None or not user.is_active:
                raise InvalidPasswordResetTokenError("Ссылка восстановления недействительна или устарела.")

            user.password_hash = hash_password(password)
            user.updated_at = now
            token.consumed_at = now
            self.session.execute(
                update(PasswordResetTokenORM)
                .where(
                    PasswordResetTokenORM.user_id == user.id,
                    PasswordResetTokenORM.consumed_at.is_(None),
                )
                .values(consumed_at=now)
            )
            self.session.execute(
                update(AuthSessionORM)
                .where(
                    AuthSessionORM.user_id == user.id,
                    AuthSessionORM.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
            self.session.commit()
        except InvalidPasswordResetTokenError:
            self.session.rollback()
            raise
        except Exception:
            self.session.rollback()
            raise
