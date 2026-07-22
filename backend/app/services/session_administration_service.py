from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.services.audit_service import AuditService
from app.services.auth_service import token_hash, utc_now


class SessionContextNotFoundError(RuntimeError):
    pass


class AccountSessionNotFoundError(RuntimeError):
    pass


class CurrentSessionRevocationError(RuntimeError):
    pass


@dataclass(frozen=True)
class AccountSessionView:
    id: int
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    is_current: bool


class SessionAdministrationService:
    def __init__(self, session: Session, *, actor: UserORM) -> None:
        self.session = session
        self.actor = actor

    def list_active(self, *, current_raw_token: str) -> list[AccountSessionView]:
        now = utc_now()
        current_token_hash = token_hash(current_raw_token)
        sessions = list(
            self.session.scalars(
                select(AuthSessionORM)
                .where(
                    AuthSessionORM.user_id == self.actor.id,
                    AuthSessionORM.revoked_at.is_(None),
                    AuthSessionORM.expires_at > now,
                )
                .order_by(AuthSessionORM.last_seen_at.desc(), AuthSessionORM.id.desc())
            ).all()
        )
        if not any(item.token_hash == current_token_hash for item in sessions):
            raise SessionContextNotFoundError("Текущая сессия больше не активна.")
        views = [
            AccountSessionView(
                id=item.id,
                created_at=item.created_at,
                last_seen_at=item.last_seen_at,
                expires_at=item.expires_at,
                is_current=item.token_hash == current_token_hash,
            )
            for item in sessions
        ]
        return sorted(
            views,
            key=lambda item: (
                not item.is_current,
                -item.last_seen_at.timestamp(),
                -item.id,
            ),
        )

    def revoke(self, session_id: int, *, current_raw_token: str) -> None:
        try:
            now = utc_now()
            current_token_hash = token_hash(current_raw_token)
            current_session = self.session.scalar(
                select(AuthSessionORM).where(
                    AuthSessionORM.user_id == self.actor.id,
                    AuthSessionORM.token_hash == current_token_hash,
                    AuthSessionORM.revoked_at.is_(None),
                    AuthSessionORM.expires_at > now,
                )
            )
            if current_session is None:
                raise SessionContextNotFoundError("Текущая сессия больше не активна.")

            target = self.session.scalar(
                select(AuthSessionORM)
                .where(
                    AuthSessionORM.id == session_id,
                    AuthSessionORM.user_id == self.actor.id,
                    AuthSessionORM.revoked_at.is_(None),
                    AuthSessionORM.expires_at > now,
                )
                .with_for_update()
            )
            if target is None:
                raise AccountSessionNotFoundError("Активная сессия не найдена.")
            if target.id == current_session.id:
                raise CurrentSessionRevocationError(
                    "Текущую сессию можно завершить только обычным выходом."
                )

            target.revoked_at = now
            AuditService(self.session).record(
                actor=self.actor,
                action="account_session_revoked",
                entity_type="auth_session",
                entity_id=target.id,
                before={"status": "active"},
                after={"status": "revoked"},
                context={"current_session_preserved": True},
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
