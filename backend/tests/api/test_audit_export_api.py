import csv
import io
import json

from fastapi import HTTPException
from sqlalchemy import func, select

from app.core.auth import require_administrator
from app.main import app
from app.models.audit_event import AuditEventORM
from app.models.user import UserORM
from app.services.audit_export_service import AuditExportService
from app.services.audit_service import AuditService


def _actor(
    *,
    email: str,
    display_name: str,
    role: str = "administrator",
) -> UserORM:
    return UserORM(
        email=email,
        display_name=display_name,
        role=role,
        password_hash="not-used",
        is_active=True,
    )


def test_filtered_audit_csv_is_utf8_safe_and_read_only(client, db_session):
    actor = _actor(
        email="audit-export@example.test",
        display_name="=2+2",
    )
    db_session.add(actor)
    db_session.flush()
    AuditService(db_session).record(
        actor=actor,
        action="audit_export_test",
        entity_type="project",
        entity_id="@project-42",
        before={
            "password_hash": "must-not-export",
            "name": "Старое название",
        },
        after={"name": "Новое название"},
        context={"changed_fields": ["name"]},
    )
    AuditService(db_session).record(
        actor=actor,
        action="other_action",
        entity_type="project",
        entity_id="42",
        after={"status": "ignored"},
    )
    db_session.commit()
    before_count = int(
        db_session.scalar(select(func.count()).select_from(AuditEventORM)) or 0
    )

    response = client.get(
        "/api/v1/audit/events/export.csv",
        params={"action": "audit_export_test", "entity_type": "project"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == (
        'attachment; filename="tourhub-audit.csv"'
    )
    assert response.headers["x-audit-event-count"] == "1"
    assert response.content.startswith(b"\xef\xbb\xbf")

    rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert len(rows) == 1
    row = rows[0]
    assert row["actor_display_name"] == "'=2+2"
    assert row["entity_id"] == "'@project-42"
    assert row["action"] == "audit_export_test"
    assert json.loads(row["before_json"]) == {"name": "Старое название"}
    assert json.loads(row["after_json"]) == {"name": "Новое название"}
    assert json.loads(row["context_json"]) == {"changed_fields": ["name"]}

    after_count = int(
        db_session.scalar(select(func.count()).select_from(AuditEventORM)) or 0
    )
    assert after_count == before_count


def test_audit_csv_export_rejects_unbounded_result(client, db_session, monkeypatch):
    actor = _actor(
        email="audit-limit@example.test",
        display_name="Audit Limit",
    )
    db_session.add(actor)
    db_session.flush()
    for entity_id in ("one", "two"):
        AuditService(db_session).record(
            actor=actor,
            action="audit_limit_test",
            entity_type="test",
            entity_id=entity_id,
        )
    db_session.commit()
    monkeypatch.setattr(AuditExportService, "max_rows", 1)

    response = client.get(
        "/api/v1/audit/events/export.csv",
        params={"action": "audit_limit_test"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == (
        "Экспорт содержит слишком много записей: 2. "
        "Уточните фильтры; максимум 1."
    )


def test_audit_csv_export_remains_administrator_only(client):
    def deny_administrator() -> None:
        raise HTTPException(status_code=403, detail="Administrator role required")

    app.dependency_overrides[require_administrator] = deny_administrator

    response = client.get("/api/v1/audit/events/export.csv")

    assert response.status_code == 403
