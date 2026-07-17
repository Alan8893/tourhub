from collections.abc import Sequence
import secrets
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_session import AuthSessionORM
from app.models.invitation import InvitationORM
from app.models.invitation_settings import InvitationSettingsORM
from app.models.user import UserORM
from app.schemas.auth import UserRole
from app.schemas.invitation import (
    InvitationAcceptRequest,
    InvitationCreateRequest,
    InvitationStatus,
)
from app.services.auth_service import hash_password, token_hash, utc_now
from app.services.invitation_settings_service import DEFAULT_VALUES


class InvitationNotFoundError(RuntimeError):
    pass


class InvitationConflictError(RuntimeError):
    pass


class InvitationPolicyError(RuntimeError):
    pass


class InvitationStateError(RuntimeError):
    pass


_STATE_MESSAGES: dict[InvitationStatus, str] = {
    InvitationStatus.EXPIRED: "Срок действия приглашения истёк.",
    InvitationStatus.REVOKED: "Приглашение отозвано администратором.",
    InvitationStatus.CONSUMED: "Приглашение уже использовано.",
    InvitationStatus.SUPERSEDED: "Приглашение заменено новой ссылкой.",
    InvitationStatus.ACTIVE: "Приглашение активно.",
}


class InvitationService:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def status_of(invitation: InvitationORM) -> InvitationStatus:
        if invitation.consumed_at is not None:
            return InvitationStatus.CONSUMED
        if invitation.revoked_at is not None:
            return InvitationStatus.REVOKED
        if invitation.superseded_at is not None:
            return InvitationStatus.SUPERSEDED
        if invitation.expires_at <= utc_now():
            return InvitationStatus.EXPIRED
        return InvitationStatus.ACTIVE

    def _settings_locked(self) -> InvitationSettingsORM:
        policy = self.session.get(InvitationSettingsORM, 1)
        if policy is None:
            policy = InvitationSettingsORM(id=1, version=1, **DEFAULT_VALUES)
            self.session.add(policy)
            self.session.flush()
        locked = self.session.scalar(
            select(InvitationSettingsORM)
            .where(InvitationSettingsORM.id == 1)
            .with_for_update()
        )
        if locked is None:
            raise RuntimeError("Invitation settings singleton is missing")
        return locked

    @staticmethod
    def _validate_domain(email: str, policy: InvitationSettingsORM) -> None:
        if not policy.allowed_email_domains:
            return
        domain = email.rsplit("@", 1)[1].encode("idna").decode("ascii")
        if domain not in policy.allowed_email_domains:
            allowed = ", ".join(policy.allowed_email_domains)
            raise InvitationPolicyError(
                f"Email-домен «{domain}» не разрешён политикой приглашений. "
                f"Разрешены: {allowed}."
            )

    def _ensure_user_absent(self, email: str) -> None:
        existing_user = self.session.scalar(
            select(UserORM.id).where(UserORM.email == email).limit(1)
        )
        if existing_user is not None:
            raise InvitationConflictError(
                "Пользователь с этим email уже существует в TourHub."
            )

    def _ensure_capacity(self, policy: InvitationSettingsORM) -> None:
        now = utc_now()
        active_count = self.session.scalar(
            select(func.count())
            .select_from(InvitationORM)
            .where(
                InvitationORM.consumed_at.is_(None),
                InvitationORM.revoked_at.is_(None),
                InvitationORM.superseded_at.is_(None),
                InvitationORM.expires_at > now,
            )
        )
        if int(active_count or 0) >= policy.active_invitation_limit:
            raise InvitationConflictError(
                "Достигнут лимит активных приглашений. Отзовите или дождитесь "
                "истечения существующего приглашения."
            )

    def _create_record(
        self,
        *,
        email: str,
        role: str,
        actor_id: int,
        policy: InvitationSettingsORM,
        reject_existing_active: bool,
    ) -> tuple[InvitationORM, str]:
        self._validate_domain(email, policy)
        self._ensure_user_absent(email)
        self._ensure_capacity(policy)
        if reject_existing_active:
            active_id = self.session.scalar(
                select(InvitationORM.id)
                .where(
                    InvitationORM.email == email,
                    InvitationORM.consumed_at.is_(None),
                    InvitationORM.revoked_at.is_(None),
                    InvitationORM.superseded_at.is_(None),
                    InvitationORM.expires_at > utc_now(),
                )
                .limit(1)
            )
            if active_id is not None:
                raise InvitationConflictError(
                    "Для этого email уже существует активное приглашение."
                )

        raw_token = secrets.token_urlsafe(32)
        invitation = InvitationORM(
            email=email,
            role=role,
            token_hash=token_hash(raw_token),
            created_by_user_id=actor_id,
            expires_at=utc_now() + timedelta(days=policy.expires_after_days),
        )
        self.session.add(invitation)
        self.session.flush()
        return invitation, raw_token

    def create(
        self,
        request: InvitationCreateRequest,
        *,
        actor: UserORM,
    ) -> tuple[InvitationORM, str]:
        policy = self._settings_locked()
        role = request.role.value if request.role is not None else policy.default_role
        invitation, raw_token = self._create_record(
            email=request.email,
            role=role,
            actor_id=actor.id,
            policy=policy,
            reject_existing_active=True,
        )
        self.session.commit()
        self.session.refresh(invitation)
        return invitation, raw_token

    def list(self, *, limit: int) -> Sequence[InvitationORM]:
        return self.session.scalars(
            select(InvitationORM).order_by(InvitationORM.id.desc()).limit(limit)
        ).all()

    def _locked_by_id(self, invitation_id: int) -> InvitationORM:
        invitation = self.session.scalar(
            select(InvitationORM)
            .where(InvitationORM.id == invitation_id)
            .with_for_update()
        )
        if invitation is None:
            raise InvitationNotFoundError("Приглашение не найдено.")
        return invitation

    def reissue(
        self,
        invitation_id: int,
        *,
        actor: UserORM,
    ) -> tuple[InvitationORM, str]:
        policy = self._settings_locked()
        if not policy.allow_resend:
            raise InvitationPolicyError(
                "Повторный выпуск приглашений отключён политикой клуба."
            )
        invitation = self._locked_by_id(invitation_id)
        current_status = self.status_of(invitation)
        if current_status in {
            InvitationStatus.CONSUMED,
            InvitationStatus.REVOKED,
            InvitationStatus.SUPERSEDED,
        }:
            raise InvitationStateError(_STATE_MESSAGES[current_status])

        invitation.superseded_at = utc_now()
        self.session.flush()
        replacement, raw_token = self._create_record(
            email=invitation.email,
            role=invitation.role,
            actor_id=actor.id,
            policy=policy,
            reject_existing_active=False,
        )
        self.session.commit()
        self.session.refresh(replacement)
        return replacement, raw_token

    def revoke(self, invitation_id: int) -> InvitationORM:
        invitation = self._locked_by_id(invitation_id)
        current_status = self.status_of(invitation)
        if current_status is not InvitationStatus.ACTIVE:
            raise InvitationStateError(_STATE_MESSAGES[current_status])
        invitation.revoked_at = utc_now()
        self.session.commit()
        self.session.refresh(invitation)
        return invitation

    def _by_raw_token(self, raw_token: str, *, lock: bool) -> InvitationORM:
        query = select(InvitationORM).where(
            InvitationORM.token_hash == token_hash(raw_token)
        )
        if lock:
            query = query.with_for_update()
        invitation = self.session.scalar(query)
        if invitation is None:
            raise InvitationNotFoundError("Приглашение недействительно.")
        current_status = self.status_of(invitation)
        if current_status is not InvitationStatus.ACTIVE:
            raise InvitationStateError(_STATE_MESSAGES[current_status])
        return invitation

    def inspect(self, raw_token: str) -> InvitationORM:
        invitation = self._by_raw_token(raw_token, lock=False)
        policy = self.session.get(InvitationSettingsORM, 1)
        if policy is not None:
            self._validate_domain(invitation.email, policy)
        return invitation

    def accept(
        self,
        request: InvitationAcceptRequest,
    ) -> tuple[UserORM, str]:
        invitation = self._by_raw_token(request.token, lock=True)
        policy = self.session.get(InvitationSettingsORM, 1)
        if policy is not None:
            self._validate_domain(invitation.email, policy)
        self._ensure_user_absent(invitation.email)

        user = UserORM(
            email=invitation.email,
            display_name=request.display_name,
            role=UserRole(invitation.role).value,
            password_hash=hash_password(request.password),
            is_active=True,
        )
        self.session.add(user)
        try:
            self.session.flush()
            invitation.consumed_at = utc_now()
            invitation.accepted_user_id = user.id
            raw_session = secrets.token_urlsafe(32)
            now = utc_now()
            self.session.add(
                AuthSessionORM(
                    user_id=user.id,
                    token_hash=token_hash(raw_session),
                    expires_at=now + timedelta(days=settings.auth.session_ttl_days),
                    last_seen_at=now,
                )
            )
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise InvitationConflictError(
                "Пользователь с этим email уже существует в TourHub."
            ) from error
        self.session.refresh(user)
        return user, raw_session
