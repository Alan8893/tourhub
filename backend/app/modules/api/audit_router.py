from dataclasses import dataclass
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.audit_event import AuditEventORM
from app.schemas.audit import AuditEventListResponse, AuditEventResponse
from app.services.audit_export_service import AUDIT_EXPORT_FILENAME, AuditExportService
from app.services.audit_service import AuditExportLimitExceededError, AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@dataclass(frozen=True)
class AuditEventQuery:
    actor_user_id: int | None
    entity_type: str | None
    entity_id: str | None
    action: str | None
    created_from: datetime | None
    created_to: datetime | None


def _audit_event_query(
    actor_user_id: int | None = Query(default=None, ge=1),
    entity_type: str | None = Query(default=None, min_length=1, max_length=64),
    entity_id: str | None = Query(default=None, min_length=1, max_length=255),
    action: str | None = Query(default=None, min_length=1, max_length=64),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
) -> AuditEventQuery:
    return AuditEventQuery(
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        created_from=created_from,
        created_to=created_to,
    )


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
    filters: AuditEventQuery = Depends(_audit_event_query),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AuditEventListResponse:
    items, total = AuditService(db).list_events(
        actor_user_id=filters.actor_user_id,
        entity_type=filters.entity_type,
        entity_id=filters.entity_id,
        action=filters.action,
        created_from=filters.created_from,
        created_to=filters.created_to,
        limit=limit,
        offset=offset,
    )
    return AuditEventListResponse(
        items=[_response(event) for event in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/events/export.csv", response_class=Response)
def export_audit_events(
    filters: AuditEventQuery = Depends(_audit_event_query),
    db: Session = Depends(get_db),
) -> Response:
    try:
        content, total = AuditExportService(db).render_csv(
            actor_user_id=filters.actor_user_id,
            entity_type=filters.entity_type,
            entity_id=filters.entity_id,
            action=filters.action,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )
    except AuditExportLimitExceededError as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                "Экспорт содержит слишком много записей: "
                f"{exc.total}. Уточните фильтры; максимум {exc.max_rows}."
            ),
        ) from exc
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{AUDIT_EXPORT_FILENAME}"',
            "X-Audit-Event-Count": str(total),
        },
    )
