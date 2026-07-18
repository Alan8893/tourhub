from datetime import datetime

from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: int
    actor_user_id: int | None
    actor_display_name: str
    actor_email: str
    actor_role: str
    action: str
    entity_type: str
    entity_id: str | None
    before_data: dict[str, object] | None
    after_data: dict[str, object] | None
    context_data: dict[str, object]
    created_at: datetime


class AuditEventListResponse(BaseModel):
    items: list[AuditEventResponse]
    total: int
    limit: int
    offset: int
