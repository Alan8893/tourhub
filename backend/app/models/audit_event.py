from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, event, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditEventORM(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    actor_display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_email: Mapped[str] = mapped_column(String(320), nullable=False)
    actor_role: Mapped[str] = mapped_column(String(32), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    before_data: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    after_data: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    context_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )


@event.listens_for(AuditEventORM, "before_update")
def _prevent_audit_update(_mapper: Any, _connection: Any, _target: AuditEventORM) -> None:
    raise RuntimeError("Audit events are immutable")


@event.listens_for(AuditEventORM, "before_delete")
def _prevent_audit_delete(_mapper: Any, _connection: Any, _target: AuditEventORM) -> None:
    raise RuntimeError("Audit events are immutable")
