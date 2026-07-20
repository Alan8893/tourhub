from typing import Literal

from sqlalchemy.orm import Session

from app.models.invitation import InvitationORM
from app.models.user import UserORM
from app.schemas.invitation import InvitationStatus
from app.services.audit_service import AuditService
from app.services.mail_delivery_service import MailDeliveryResult

_UNSET = object()


class InvitationAuditService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record_created(self, *, actor: UserORM, invitation: InvitationORM) -> None:
        AuditService(self.session).record(
            actor=actor,
            action="invitation_created",
            entity_type="invitation",
            entity_id=invitation.id,
            after=self._snapshot(invitation, status=InvitationStatus.ACTIVE),
        )

    def record_reissued(
        self,
        *,
        actor: UserORM,
        previous: InvitationORM,
        previous_status: InvitationStatus,
        replacement: InvitationORM,
    ) -> None:
        AuditService(self.session).record(
            actor=actor,
            action="invitation_reissued",
            entity_type="invitation",
            entity_id=replacement.id,
            before=self._snapshot(previous, status=previous_status),
            after=self._snapshot(replacement, status=InvitationStatus.ACTIVE),
            context={"superseded_invitation_id": previous.id},
        )

    def record_revoked(
        self,
        *,
        actor: UserORM,
        invitation: InvitationORM,
        before_status: InvitationStatus,
    ) -> None:
        AuditService(self.session).record(
            actor=actor,
            action="invitation_revoked",
            entity_type="invitation",
            entity_id=invitation.id,
            before=self._snapshot(invitation, status=before_status),
            after=self._snapshot(invitation, status=InvitationStatus.REVOKED),
        )

    def record_accepted(
        self,
        *,
        actor: UserORM,
        invitation: InvitationORM,
        before_status: InvitationStatus,
    ) -> None:
        AuditService(self.session).record(
            actor=actor,
            action="invitation_accepted",
            entity_type="invitation",
            entity_id=invitation.id,
            before=self._snapshot(
                invitation,
                status=before_status,
                accepted_user_id=None,
            ),
            after=self._snapshot(invitation, status=InvitationStatus.CONSUMED),
            context={"created_user_id": actor.id},
        )

    def record_delivery_result(
        self,
        *,
        actor: UserORM,
        invitation: InvitationORM,
        operation: Literal["create", "reissue"],
        result: MailDeliveryResult,
    ) -> None:
        AuditService(self.session).record(
            actor=actor,
            action="invitation_delivery_result",
            entity_type="invitation",
            entity_id=invitation.id,
            after={
                "status": result.status.value,
                "attempts": result.attempts,
                "recipient_domain": self._recipient_domain(invitation.email),
            },
            context={
                "operation": operation,
                "role": invitation.role,
            },
        )
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    @classmethod
    def _snapshot(
        cls,
        invitation: InvitationORM,
        *,
        status: InvitationStatus,
        accepted_user_id: int | None | object = _UNSET,
    ) -> dict[str, object]:
        resolved_accepted_user_id = (
            invitation.accepted_user_id
            if accepted_user_id is _UNSET
            else accepted_user_id
        )
        return {
            "recipient_domain": cls._recipient_domain(invitation.email),
            "role": invitation.role,
            "status": status.value,
            "expires_at": invitation.expires_at,
            "created_by_user_id": invitation.created_by_user_id,
            "accepted_user_id": resolved_accepted_user_id,
        }

    @staticmethod
    def _recipient_domain(email: str) -> str:
        return email.rsplit("@", 1)[-1].casefold()
