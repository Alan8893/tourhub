import csv
import io
import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEventORM
from app.services.audit_service import AuditService

AUDIT_EXPORT_MAX_ROWS = 10_000
AUDIT_EXPORT_FILENAME = "tourhub-audit.csv"
AUDIT_EXPORT_HEADERS = (
    "id",
    "created_at",
    "actor_user_id",
    "actor_display_name",
    "actor_email",
    "actor_role",
    "action",
    "entity_type",
    "entity_id",
    "before_json",
    "after_json",
    "context_json",
)
_FORMULA_PREFIXES = ("=", "+", "-", "@")


class AuditExportService:
    max_rows = AUDIT_EXPORT_MAX_ROWS

    def __init__(self, session: Session) -> None:
        self.audit_service = AuditService(session)

    def render_csv(
        self,
        *,
        actor_user_id: int | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
    ) -> tuple[bytes, int]:
        events, total = self.audit_service.export_events(
            actor_user_id=actor_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            created_from=created_from,
            created_to=created_to,
            max_rows=self.max_rows,
        )
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer, lineterminator="\r\n")
        writer.writerow(AUDIT_EXPORT_HEADERS)
        for event in events:
            writer.writerow(self._row(event))
        return ("\ufeff" + buffer.getvalue()).encode("utf-8"), total

    @classmethod
    def _row(cls, event: AuditEventORM) -> tuple[str, ...]:
        return (
            cls._cell(event.id),
            cls._cell(event.created_at.isoformat()),
            cls._cell(event.actor_user_id),
            cls._cell(event.actor_display_name),
            cls._cell(event.actor_email),
            cls._cell(event.actor_role),
            cls._cell(event.action),
            cls._cell(event.entity_type),
            cls._cell(event.entity_id),
            cls._json_cell(event.before_data),
            cls._json_cell(event.after_data),
            cls._json_cell(event.context_data),
        )

    @classmethod
    def _json_cell(cls, value: dict[str, object] | None) -> str:
        if value is None:
            return ""
        return cls._cell(
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )

    @staticmethod
    def _cell(value: object | None) -> str:
        if value is None:
            return ""
        text = str(value)
        if text.lstrip().startswith(_FORMULA_PREFIXES):
            return "'" + text
        return text
