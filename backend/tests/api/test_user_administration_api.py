from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.services.auth_service import hash_password, utc_now

ADMIN_PAYLOAD = {
    "email": "admin@tourhub.local",
    "display_name": "Локальный администратор",
    "password": "correct-horse-battery-staple",
}


def bootstrap(client) -> dict:
    response = client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD)
    assert response.status_code == 201, response.text
    return response.json()["user"]


def add_user(
    db_session,
    *,
    email: str,
    role: str = "instructor",
    is_active: bool = True,
) -> UserORM:
    user = UserORM(
        email=email,
        display_name=email.split("@", 1)[0].replace(".", " ").title(),
        role=role,
        password_hash=hash_password("member-password-12345"),
        is_active=is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def current_role(client: TestClient) -> str:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200, response.text
    return response.json()["user"]["role"]


def test_user_list_requires_administrator_and_exposes_safe_fields(
    auth_client,
    db_session,
) -> None:
    assert auth_client.get("/api/v1/users").status_code == 401
    current = bootstrap(auth_client)
    add_user(db_session, email="member@example.org")

    response = auth_client.get("/api/v1/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert any(item["id"] == current["id"] and item["is_current"] for item in users)
    assert "password_hash" not in str(users)
    assert "token_hash" not in str(users)

    administrator = db_session.get(UserORM, current["id"])
    assert administrator is not None
    administrator.role = "instructor"
    db_session.commit()
    assert auth_client.get("/api/v1/users").status_code == 403


def test_last_active_administrator_cannot_be_demoted_or_deactivated(
    auth_client,
    db_session,
) -> None:
    current = bootstrap(auth_client)
    listed = auth_client.get("/api/v1/users").json()[0]

    demotion = auth_client.patch(
        f"/api/v1/users/{current['id']}",
        json={
            "expected_version": listed["version"],
            "role": "instructor",
            "is_active": True,
        },
    )
    assert demotion.status_code == 409
    assert "последнего активного администратора" in demotion.json()["error"]

    deactivation = auth_client.patch(
        f"/api/v1/users/{current['id']}",
        json={
            "expected_version": listed["version"],
            "role": "administrator",
            "is_active": False,
        },
    )
    assert deactivation.status_code == 409

    db_session.expire_all()
    administrator = db_session.get(UserORM, current["id"])
    assert administrator is not None
    assert administrator.role == "administrator"
    assert administrator.is_active is True
    assert administrator.version == listed["version"]


def test_role_and_activation_updates_use_versions_and_revoke_sessions(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    member = add_user(db_session, email="member@example.org")
    now = utc_now()
    session = AuthSessionORM(
        user_id=member.id,
        token_hash="a" * 64,
        expires_at=now + timedelta(days=7),
        last_seen_at=now,
    )
    db_session.add(session)
    db_session.commit()

    updated = auth_client.patch(
        f"/api/v1/users/{member.id}",
        json={
            "expected_version": member.version,
            "role": "verified_instructor",
            "is_active": False,
        },
    )
    assert updated.status_code == 200, updated.text
    body = updated.json()
    assert body["role"] == "verified_instructor"
    assert body["is_active"] is False
    assert body["version"] == 2

    db_session.expire_all()
    stored_session = db_session.scalar(
        select(AuthSessionORM).where(AuthSessionORM.user_id == member.id)
    )
    assert stored_session is not None and stored_session.revoked_at is not None

    stale = auth_client.patch(
        f"/api/v1/users/{member.id}",
        json={
            "expected_version": 1,
            "role": "instructor",
            "is_active": True,
        },
    )
    assert stale.status_code == 409

    reactivated = auth_client.patch(
        f"/api/v1/users/{member.id}",
        json={
            "expected_version": body["version"],
            "role": "instructor",
            "is_active": True,
        },
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["version"] == 3


def test_self_demotion_is_allowed_when_another_active_administrator_exists(
    auth_client,
    db_session,
) -> None:
    current = bootstrap(auth_client)
    add_user(
        db_session,
        email="second.admin@example.org",
        role="administrator",
    )
    current_record = next(
        item for item in auth_client.get("/api/v1/users").json() if item["is_current"]
    )

    response = auth_client.patch(
        f"/api/v1/users/{current['id']}",
        json={
            "expected_version": current_record["version"],
            "role": "instructor",
            "is_active": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["role"] == "instructor"
    assert auth_client.get("/api/v1/auth/me").json()["user"]["role"] == "instructor"
    assert auth_client.get("/api/v1/users").status_code == 403


def test_role_changes_reach_all_sessions_and_deactivation_revokes_them(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    member = add_user(db_session, email="multi.session@example.org")
    login_payload = {
        "email": member.email,
        "password": "member-password-12345",
    }
    first_client = TestClient(app)
    second_client = TestClient(app)

    try:
        first_login = first_client.post("/api/v1/auth/login", json=login_payload)
        second_login = second_client.post("/api/v1/auth/login", json=login_payload)
        assert first_login.status_code == 200, first_login.text
        assert second_login.status_code == 200, second_login.text
        assert current_role(first_client) == "instructor"
        assert current_role(second_client) == "instructor"

        promoted = auth_client.patch(
            f"/api/v1/users/{member.id}",
            json={
                "expected_version": member.version,
                "role": "verified_instructor",
                "is_active": True,
            },
        )
        assert promoted.status_code == 200, promoted.text
        promoted_body = promoted.json()
        assert promoted_body["version"] == 2
        assert current_role(first_client) == "verified_instructor"
        assert current_role(second_client) == "verified_instructor"

        deactivated = auth_client.patch(
            f"/api/v1/users/{member.id}",
            json={
                "expected_version": promoted_body["version"],
                "role": "verified_instructor",
                "is_active": False,
            },
        )
        assert deactivated.status_code == 200, deactivated.text
        assert first_client.get("/api/v1/auth/me").status_code == 401
        assert second_client.get("/api/v1/auth/me").status_code == 401
    finally:
        first_client.close()
        second_client.close()

    db_session.expire_all()
    sessions = db_session.scalars(
        select(AuthSessionORM).where(AuthSessionORM.user_id == member.id)
    ).all()
    assert len(sessions) == 2
    assert all(session.revoked_at is not None for session in sessions)
