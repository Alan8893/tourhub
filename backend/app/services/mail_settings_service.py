import os
from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.mail_settings import MailSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.mail_settings import MailSettingsUpdateRequest
from app.services.club_settings_service import SettingsVersionConflictError

LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200
MAIL_SECRET_ENV_VAR = "TOURHUB_SMTP_SECRET"

DEFAULT_VALUES: dict[str, object] = {
    "smtp_host": "localhost",
    "smtp_port": 587,
    "security_mode": "starttls",
    "smtp_username": None,
    "sender_email": "tourhub@localhost",
    "sender_name": "TourHub",
    "reply_to_email": None,
    "test_recipient_email": None,
    "timeout_seconds": 30,
    "retry_count": 3,
}


class MailSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> MailSettingsORM:
        settings = self.session.get(MailSettingsORM, 1)
        if settings is not None:
            return settings

        settings = MailSettingsORM(id=1, version=1, **DEFAULT_VALUES)
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(self, request: MailSettingsUpdateRequest) -> MailSettingsORM:
        self.get()
        settings = self.session.scalar(
            select(MailSettingsORM)
            .where(MailSettingsORM.id == 1)
            .with_for_update()
        )
        if settings is None:
            raise RuntimeError("Mail settings singleton is missing")
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        normalized: dict[str, object] = {
            "smtp_host": request.smtp_host,
            "smtp_port": request.smtp_port,
            "security_mode": request.security_mode.value,
            "smtp_username": request.smtp_username,
            "sender_email": request.sender_email,
            "sender_name": request.sender_name,
            "reply_to_email": request.reply_to_email,
            "test_recipient_email": request.test_recipient_email,
            "timeout_seconds": request.timeout_seconds,
            "retry_count": request.retry_count,
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
                section="mail",
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
            .where(SystemSettingsHistoryORM.section == "mail")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        ).all()

    @staticmethod
    def secret_configured() -> bool:
        value = os.getenv(MAIL_SECRET_ENV_VAR)
        return bool(value and value.strip())

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
