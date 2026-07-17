from sqlalchemy import select

from app.core.config import settings
from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM

ADMIN_PAYLOAD = {
    "email": " Admin@TourHub.Local ",
    "display_name": "  Локальный   администратор  ",
    "password": "correct-horse-battery-staple",
}


def test_bootstrap_creates_one_administrator_and_server_session(auth_client, db_session) -> None:
    status = auth_client.get("/api/v1/auth/bootstrap-status")
    assert status.status_code == 200
    assert status.json() == {"bootstrap_required": True}

    response = auth_client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "admin@tourhub.local"
    assert body["user"]["display_name"] == "Локальный администратор"
    assert body["user"]["role"] == "administrator"
    assert "password" not in str(body).lower()

    cookie_header = response.headers["set-cookie"]
    assert settings.auth.session_cookie_name in cookie_header
    assert "HttpOnly" in cookie_header
    assert "SameSite=lax" in cookie_header

    raw_token = auth_client.cookies.get(settings.auth.session_cookie_name)
    assert raw_token
    user = db_session.scalar(select(UserORM))
    session = db_session.scalar(select(AuthSessionORM))
    assert user is not None
    assert user.password_hash != ADMIN_PAYLOAD["password"]
    assert ADMIN_PAYLOAD["password"] not in user.password_hash
    assert session is not None
    assert session.token_hash != raw_token
    assert raw_token not in session.token_hash

    current = auth_client.get("/api/v1/auth/me")
    assert current.status_code == 200
    assert current.json()["user"]["role"] == "administrator"
    assert auth_client.get("/api/v1/settings/appearance").status_code == 200
    assert auth_client.get("/api/v1/auth/bootstrap-status").json() == {
        "bootstrap_required": False
    }


def test_duplicate_bootstrap_is_rejected_without_second_user(auth_client, db_session) -> None:
    assert auth_client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD).status_code == 201
    response = auth_client.post(
        "/api/v1/auth/bootstrap",
        json={**ADMIN_PAYLOAD, "email": "second@example.org"},
    )
    assert response.status_code == 409
    assert "уже создан" in response.json()["error"]
    assert len(db_session.scalars(select(UserORM)).all()) == 1


def test_login_uses_generic_error_and_logout_revokes_session(auth_client, db_session) -> None:
    assert auth_client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD).status_code == 201
    auth_client.post("/api/v1/auth/logout")

    unknown = auth_client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.org", "password": "incorrect-password"},
    )
    wrong = auth_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tourhub.local", "password": "incorrect-password"},
    )
    assert unknown.status_code == 401
    assert wrong.status_code == 401
    assert unknown.json()["error"] == wrong.json()["error"]

    login = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "ADMIN@TOURHUB.LOCAL",
            "password": ADMIN_PAYLOAD["password"],
        },
    )
    assert login.status_code == 200
    assert auth_client.get("/api/v1/auth/me").status_code == 200

    raw_token = auth_client.cookies.get(settings.auth.session_cookie_name)
    assert raw_token
    logout = auth_client.post("/api/v1/auth/logout")
    assert logout.status_code == 204
    assert auth_client.get("/api/v1/auth/me").status_code == 401
    sessions = db_session.scalars(select(AuthSessionORM)).all()
    assert any(item.revoked_at is not None for item in sessions)


def test_settings_require_authenticated_administrator(auth_client, db_session) -> None:
    assert auth_client.get("/api/v1/settings/appearance").status_code == 401
    assert auth_client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD).status_code == 201

    user = db_session.scalar(select(UserORM))
    assert user is not None
    user.role = "instructor"
    db_session.commit()

    response = auth_client.get("/api/v1/settings/appearance")
    assert response.status_code == 403
    assert "администратор" in response.json()["error"].lower()
