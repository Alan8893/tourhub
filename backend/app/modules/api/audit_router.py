from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.audit_event import AuditEventORM
from app.schemas.audit import AuditEventListResponse, AuditEventResponse
from app.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


def _response(event: AuditEventORM) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        actor_user_id=event.actor_user_id,
        actor_display_name=event.actor_display_name,
        actor_email=event.actor_email,
        actor_role=event.actor_role,
        action=event.action,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        before_data=event.before_data,
        after_data=event.after_data,
        context_data=event.context_data,
        created_at=event.created_at,
    )


@router.get("/events", response_model=AuditEventListResponse)
def list_audit_events(
    actor_user_id: int | None = Query(default=None, ge=1),
    entity_type: str | None = Query(default=None, min_length=1, max_length=64),
    entity_id: str | None = Query(default=None, min_length=1, max_length=255),
    action: str | None = Query(default=None, min_length=1, max_length=64),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AuditEventListResponse:
    items, total = AuditService(db).list_events(
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )
    return AuditEventListResponse(
        items=[_response(event) for event in items],
        total=total,
        limit=limit,
        offset=offset,
    )
