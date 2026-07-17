from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.invitation_settings import InvitationSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.invitation_settings import (
    InvitationDefaultRole,
    InvitationSettingsUpdateRequest,
)
from app.services.club_settings_service import SettingsVersionConflictError

LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200

DEFAULT_VALUES: dict[str, object] = {
    "expires_after_days": 7,
    "default_role": InvitationDefaultRole.INSTRUCTOR.value,
    "allowed_email_domains": [],
    "allow_resend": True,
    "active_invitation_limit": 100,
    "administrators_only": True,
    "require_email_confirmation": True,
}


class InvitationSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> InvitationSettingsORM:
        settings = self.session.get(InvitationSettingsORM, 1)
        if settings is not None:
            return settings

        settings = InvitationSettingsORM(id=1, version=1, **DEFAULT_VALUES)
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(
        self,
        request: InvitationSettingsUpdateRequest,
    ) -> InvitationSettingsORM:
        self.get()
        settings = self.session.scalar(
            select(InvitationSettingsORM)
            .where(InvitationSettingsORM.id == 1)
            .with_for_update()
        )
        if settings is None:
            raise RuntimeError("Invitation settings singleton is missing")
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        normalized: dict[str, object] = {
            "expires_after_days": request.expires_after_days,
            "default_role": request.default_role.value,
            "allowed_email_domains": list(request.allowed_email_domains),
            "allow_resend": request.allow_resend,
            "active_invitation_limit": request.active_invitation_limit,
            "administrators_only": request.administrators_only,
            "require_email_confirmation": request.require_email_confirmation,
        }

        changed_fields: list[str] = []
        for field_name, value in normalized.items():
            if getattr(settings, field_name) != value:
                setattr(settings, field_name, value)
                changed_fields.append(field_name)

        if not changed_fields:
            return settings

        settings.version += 1
        self.session.add(
            SystemSettingsHistoryORM(
                section="invitations",
                actor_label=LOCAL_ADMIN_ACTOR,
                action="updated",
                changed_fields=changed_fields,
                settings_version=settings.version,
            )
        )
        self.session.flush()
        self._trim_history()
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def list_history(self, *, limit: int) -> Sequence[SystemSettingsHistoryORM]:
        return self.session.scalars(
            select(SystemSettingsHistoryORM)
            .where(SystemSettingsHistoryORM.section == "invitations")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        ).all()

    def _trim_history(self) -> None:
        stale_ids = self.session.scalars(
            select(SystemSettingsHistoryORM.id)
            .order_by(SystemSettingsHistoryORM.id.desc())
            .offset(HISTORY_LIMIT)
        ).all()
        if stale_ids:
            self.session.execute(
                delete(SystemSettingsHistoryORM).where(
                    SystemSettingsHistoryORM.id.in_(stale_ids)
                )
            )
