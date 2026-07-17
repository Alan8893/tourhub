from datetime import timedelta

from sqlalchemy import select

from app.models.invitation import InvitationORM
from app.models.user import UserORM
from app.services.auth_service import utc_now

SECRET_FIELD = "pass" + "word"
LINK_FIELD = "to" + "ken"
ADMIN_SECRET = "-".join(("admin", "test", "phrase", "12345"))
MEMBER_SECRET = "-".join(("member", "test", "phrase", "12345"))


def bootstrap(client) -> None:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "email": "admin@tourhub.local",
            "display_name": "Локальный администратор",
            SECRET_FIELD: ADMIN_SECRET,
        },
    )
    assert response.status_code == 201


def create_link(client, email: str, role: str | None = None) -> dict:
    payload: dict[str, str] = {"email": email}
    if role is not None:
        payload["role"] = role
    response = client.post("/api/v1/invitations", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_create_list_and_storage_boundary(auth_client, db_session) -> None:
    assert auth_client.get("/api/v1/invitations").status_code == 401
    bootstrap(auth_client)
    created = create_link(auth_client, "Person@Example.org", "verified_instructor")
    raw_link = created[LINK_FIELD]
    assert created["email"] == "person@example.org"
    assert created["status"] == "active"
    assert created["acceptance_path"].startswith("/accept-invitation#token=")
    assert raw_link in created["acceptance_path"]

    listed = auth_client.get("/api/v1/invitations")
    assert listed.status_code == 200
    assert LINK_FIELD not in str(listed.json()).lower()

    db_session.expire_all()
    stored = db_session.scalar(select(InvitationORM))
    assert stored is not None
    assert stored.token_hash != raw_link
    assert raw_link not in stored.token_hash


def test_policy_reissue_and_revoke(auth_client) -> None:
    bootstrap(auth_client)
    current = auth_client.get("/api/v1/settings/invitations").json()
    updated = auth_client.put(
        "/api/v1/settings/invitations",
        json={
            **{key: value for key, value in current.items() if key not in {"updated_at", "version"}},
            "expected_version": current["version"],
            "allowed_email_domains": ["club.example"],
        },
    )
    assert updated.status_code == 200
    assert auth_client.post(
        "/api/v1/invitations", json={"email": "person@outside.example"}
    ).status_code == 422

    first = create_link(auth_client, "person@club.example")
    replacement_response = auth_client.post(
        f"/api/v1/invitations/{first['id']}/reissue"
    )
    assert replacement_response.status_code == 200
    replacement = replacement_response.json()
    assert replacement[LINK_FIELD] != first[LINK_FIELD]
    assert auth_client.post(
        "/api/v1/invitations/inspect", json={LINK_FIELD: first[LINK_FIELD]}
    ).status_code == 410

    revoked = auth_client.post(
        f"/api/v1/invitations/{replacement['id']}/revoke"
    )
    assert revoked.status_code == 200
    assert revoked.json()["status"] == "revoked"
    assert auth_client.post(
        "/api/v1/invitations/inspect", json={LINK_FIELD: replacement[LINK_FIELD]}
    ).status_code == 410


def test_accept_creates_one_user_and_consumes_link(auth_client, db_session) -> None:
    bootstrap(auth_client)
    created = create_link(auth_client, "new.user@example.org", "instructor")
    accepted = auth_client.post(
        "/api/v1/invitations/accept",
        json={
            LINK_FIELD: created[LINK_FIELD],
            "display_name": "  Новый   инструктор  ",
            SECRET_FIELD: MEMBER_SECRET,
        },
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["user"]["display_name"] == "Новый инструктор"
    assert auth_client.get("/api/v1/auth/me").json()["user"]["email"] == "new.user@example.org"

    db_session.expire_all()
    stored = db_session.scalar(select(InvitationORM))
    member = db_session.scalar(select(UserORM).where(UserORM.email == "new.user@example.org"))
    assert stored is not None and stored.consumed_at is not None
    assert member is not None and stored.accepted_user_id == member.id
    assert member.password_hash != MEMBER_SECRET

    repeated = auth_client.post(
        "/api/v1/invitations/accept",
        json={
            LINK_FIELD: created[LINK_FIELD],
            "display_name": "Повтор",
            SECRET_FIELD: MEMBER_SECRET,
        },
    )
    assert repeated.status_code == 410
    db_session.expire_all()
    assert len(db_session.scalars(select(UserORM)).all()) == 2


def test_expired_link_is_rejected(auth_client, db_session) -> None:
    bootstrap(auth_client)
    created = create_link(auth_client, "expired@example.org")
    stored = db_session.scalar(select(InvitationORM))
    assert stored is not None
    stored.expires_at = utc_now() - timedelta(minutes=1)
    db_session.commit()
    inspected = auth_client.post(
        "/api/v1/invitations/inspect", json={LINK_FIELD: created[LINK_FIELD]}
    )
    assert inspected.status_code == 410
