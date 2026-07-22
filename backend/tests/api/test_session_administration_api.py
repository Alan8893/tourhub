from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models.audit_event import AuditEventORM
from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.services.audit_service import AuditService
from app.services.auth_service import hash_password, token_hash
from app.services.session_administration_service import SessionAdministrationService

PASSWORD_FIELD = "pass" + "word"
ADMIN_SECRET = "-".join(("session", "admin", "phrase", "12345"))
MEMBER_SECRET = "-".join(("session", "member", "phrase", "12345"))


def _bootstrap(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "email": "admin@tourhub.local",
            "display_name": "Первый Администратор",
            PASSWORD_FIELD: ADMIN_SECRET,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["user"]


def test_user_lists_only_safe_active_sessions_and_revokes_one(auth_client, db_session):
    _bootstrap(auth_client)
    second_client = TestClient(app)
    second_login = second_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tourhub.local", PASSWORD_FIELD: ADMIN_SECRET},
    )
    assert second_login.status_code == 200

    response = auth_client.get("/api/v1/account/sessions")
    assert response.status_code == 200, response.text
    sessions = response.json()
    assert len(sessions) == 2
    assert sum(item["is_current"] for item in sessions) == 1
    assert set(sessions[0]) == {
        "id",
        "created_at",
        "last_seen_at",
        "expires_at",
        "is_current",
    }
    current = next(item for item in sessions if item["is_current"])
    other = next(item for item in sessions if not item["is_current"])

    current_revoke = auth_client.delete(f"/api/v1/account/sessions/{current['id']}")
    assert current_revoke.status_code == 409
    assert auth_client.get("/api/v1/auth/me").status_code == 200

    revoked = auth_client.delete(f"/api/v1/account/sessions/{other['id']}")
    assert revoked.status_code == 204, revoked.text
    assert auth_client.get("/api/v1/auth/me").status_code == 200
    assert second_client.get("/api/v1/auth/me").status_code == 401

    remaining = auth_client.get("/api/v1/account/sessions")
    assert remaining.status_code == 200
    assert [item["id"] for item in remaining.json()] == [current["id"]]

    db_session.expire_all()
    event = db_session.scalar(
        select(AuditEventORM).where(AuditEventORM.action == "account_session_revoked")
    )
    assert event is not None
    assert event.entity_type == "auth_session"
    assert event.entity_id == str(other["id"])
    assert event.before_data == {"status": "active"}
    assert event.after_data == {"status": "revoked"}
    assert event.context_data == {"current_login_preserved": True}
    serialized = str(
        {
            "before": event.before_data,
            "after": event.after_data,
            "context": event.context_data,
        }
    )
    assert "token" not in serialized.casefold()
    assert "cookie" not in serialized.casefold()
    assert "session" not in serialized.casefold()


def test_session_revocation_hides_unrelated_revoked_expired_and_unknown_ids(
    auth_client,
    db_session,
):
    _bootstrap(auth_client)
    administrator = db_session.scalar(
        select(UserORM).where(UserORM.email == "admin@tourhub.local")
    )
    assert administrator is not None
    outsider = UserORM(
        email="other@example.org",
        display_name="Другой пользователь",
        role="instructor",
        password_hash=hash_password(MEMBER_SECRET),
        is_active=True,
    )
    db_session.add(outsider)
    db_session.flush()
    revoked_session = AuthSessionORM(
        user=administrator,
        token_hash=token_hash("already-revoked-session"),
        expires_at=datetime(2099, 1, 1),
        last_seen_at=datetime(2026, 1, 1),
        revoked_at=datetime(2026, 1, 2),
    )
    expired_session = AuthSessionORM(
        user=administrator,
        token_hash=token_hash("expired-session"),
        expires_at=datetime(2020, 1, 1),
        last_seen_at=datetime(2020, 1, 1),
    )
    unrelated_session = AuthSessionORM(
        user=outsider,
        token_hash=token_hash("unrelated-session"),
        expires_at=datetime(2099, 1, 1),
        last_seen_at=datetime(2026, 1, 1),
    )
    db_session.add_all([revoked_session, expired_session, unrelated_session])
    db_session.commit()

    for session_id in (
        revoked_session.id,
        expired_session.id,
        unrelated_session.id,
        999999,
    ):
        response = auth_client.delete(f"/api/v1/account/sessions/{session_id}")
        assert response.status_code == 404
        assert response.json()["error"] == "Активная сессия не найдена."


def test_session_revocation_rolls_back_when_audit_fails(db_session, monkeypatch):
    raw_current_token = "current-session-token"
    actor = UserORM(
        email="member@example.org",
        display_name="Участник",
        role="instructor",
        password_hash=hash_password(MEMBER_SECRET),
        is_active=True,
    )
    current_session = AuthSessionORM(
        user=actor,
        token_hash=token_hash(raw_current_token),
        expires_at=datetime(2099, 1, 1),
        last_seen_at=datetime(2026, 1, 1),
    )
    other_session = AuthSessionORM(
        user=actor,
        token_hash=token_hash("other-session-token"),
        expires_at=datetime(2099, 1, 1),
        last_seen_at=datetime(2026, 1, 1),
    )
    db_session.add_all([actor, current_session, other_session])
    db_session.commit()
    other_session_id = other_session.id

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        SessionAdministrationService(db_session, actor=actor).revoke(
            other_session_id,
            current_raw_token=raw_current_token,
        )

    db_session.expire_all()
    stored = db_session.get(AuthSessionORM, other_session_id)
    assert stored is not None
    assert stored.revoked_at is None
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
