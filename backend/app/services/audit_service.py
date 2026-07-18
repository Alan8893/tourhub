from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEventORM
from app.models.user import UserORM

_SENSITIVE_KEY_PARTS = (
    "authorization",
    "cookie",
    "credential",
    "hash",
    "password",
    "secret",
    "session",
    "token",
)
_MAX_DEPTH = 4
_MAX_ITEMS = 50
_MAX_STRING_LENGTH = 500


class AuditService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record(
        self,
        *,
        actor: UserORM,
        action: str,
        entity_type: str,
        entity_id: str | int | None,
        before: Mapping[str, object] | None = None,
        after: Mapping[str, object] | None = None,
        context: Mapping[str, object] | None = None,
    ) -> AuditEventORM:
        event = AuditEventORM(
            actor_user_id=actor.id,
            actor_display_name=actor.display_name,
            actor_email=actor.email,
            actor_role=actor.role,
            action=self._required_text(action, "Audit action", max_length=64),
            entity_type=self._required_text(
                entity_type,
                "Audit entity type",
                max_length=64,
            ),
            entity_id=self._optional_text(entity_id, max_length=255),
            before_data=self._sanitize_mapping(before),
            after_data=self._sanitize_mapping(after),
            context_data=self._sanitize_mapping(context) or {},
        )
        self.session.add(event)
        return event

    def list_events(
        self,
        *,
        actor_user_id: int | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AuditEventORM], int]:
        filters = []
        if actor_user_id is not None:
            filters.append(AuditEventORM.actor_user_id == actor_user_id)
        if entity_type is not None:
            filters.append(AuditEventORM.entity_type == entity_type)
        if entity_id is not None:
            filters.append(AuditEventORM.entity_id == entity_id)
        if action is not None:
            filters.append(AuditEventORM.action == action)
        if created_from is not None:
            filters.append(AuditEventORM.created_at >= created_from)
        if created_to is not None:
            filters.append(AuditEventORM.created_at <= created_to)

        statement = (
            select(AuditEventORM)
            .where(*filters)
            .order_by(AuditEventORM.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = select(func.count()).select_from(AuditEventORM).where(*filters)
        items = list(self.session.scalars(statement).all())
        total = int(self.session.scalar(count_statement) or 0)
        return items, total

    @classmethod
    def _sanitize_mapping(
        cls,
        value: Mapping[str, object] | None,
    ) -> dict[str, object] | None:
        if value is None:
            return None
        sanitized: dict[str, object] = {}
        for key, item in list(value.items())[:_MAX_ITEMS]:
            normalized_key = str(key)[:128]
            if cls._is_sensitive_key(normalized_key):
                continue
            sanitized[normalized_key] = cls._safe_value(item, depth=1)
        return sanitized

    @classmethod
    def _safe_value(cls, value: object, *, depth: int) -> object:
        if depth > _MAX_DEPTH:
            return "<truncated>"
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return value[:_MAX_STRING_LENGTH]
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, Enum):
            return cls._safe_value(value.value, depth=depth + 1)
        if isinstance(value, bytes):
            return f"<bytes:{len(value)}>"
        if isinstance(value, Mapping):
            nested: dict[str, object] = {}
            for key, item in list(value.items())[:_MAX_ITEMS]:
                normalized_key = str(key)[:128]
                if cls._is_sensitive_key(normalized_key):
                    continue
                nested[normalized_key] = cls._safe_value(item, depth=depth + 1)
            return nested
        if isinstance(value, Sequence):
            return [
                cls._safe_value(item, depth=depth + 1)
                for item in list(value)[:_MAX_ITEMS]
            ]
        return str(value)[:_MAX_STRING_LENGTH]

    @staticmethod
    def _is_sensitive_key(key: str) -> bool:
        normalized = key.casefold()
        return any(part in normalized for part in _SENSITIVE_KEY_PARTS)

    @staticmethod
    def _required_text(value: str, field_name: str, *, max_length: int) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty")
        if len(normalized) > max_length:
            raise ValueError(f"{field_name} is too long")
        return normalized

    @staticmethod
    def _optional_text(value: str | int | None, *, max_length: int) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            return None
        return normalized[:max_length]
