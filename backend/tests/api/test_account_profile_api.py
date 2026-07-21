from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.models.audit_event import AuditEventORM
from app.models.auth_session import AuthSessionORM
from app.models.user import UserORM
from app.schemas.account_profile import AccountProfileUpdateRequest
from app.services.account_profile_service import AccountProfileService
from app.services.audit_service import AuditService
from app.services.auth_service import hash_password

PASSWORD_FIELD = "pass" + "word"
ADMIN_SECRET = "-".join(("account", "admin", "phrase", "12345"))
NEW_SECRET = "-".join(("account", "updated", "phrase", "67890"))
MEMBER_SECRET = "-".join(("account", "member", "phrase", "12345"))


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


def _profile_payload(*, version: int, display_name: str = "Анна Администратор"):
    return {
        "display_name": display_name,
        "phone": "+7 (999) 123-45-67",
        "telegram_url": "@anna_guide",
        "max_url": "max.ru/anna.guide",
        "vk_url": "https://vk.ru/anna-guide/",
        "version": version,
    }


def _event(db_session, action: str) -> AuditEventORM | None:
    db_session.expire_all()
    return db_session.scalar(
        select(AuditEventORM).where(AuditEventORM.action == action)
    )


def _event_text(event: AuditEventORM) -> str:
    return str(
        {
            "before": event.before_data,
            "after": event.after_data,
            "context": event.context_data,
        }
    )


def test_profile_update_normalizes_contacts_and_audits_only_changed_fields(
    auth_client,
    db_session,
):
    user = _bootstrap(auth_client)
    response = auth_client.patch(
        "/api/v1/account",
        json=_profile_payload(version=int(user["version"] if "version" in user else 1)),
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["display_name"] == "Анна Администратор"
    assert payload["email"] == "admin@tourhub.local"
    assert payload["phone"] == "+79991234567"
    assert payload["telegram_url"] == "https://t.me/anna_guide"
    assert payload["max_url"] == "https://max.ru/anna.guide"
    assert payload["vk_url"] == "https://vk.com/anna-guide"
    assert payload["version"] == 2

    event = _event(db_session, "account_profile_updated")
    assert event is not None
    assert event.actor_user_id == payload["id"]
    assert event.actor_display_name == "Анна Администратор"
    assert event.entity_type == "user"
    assert event.entity_id == str(payload["id"])
    assert event.before_data == {"version": 1}
    assert event.after_data == {"version": 2}
    assert event.context_data == {
        "changed_fields": [
            "display_name",
            "phone",
            "telegram_url",
            "max_url",
            "vk_url",
        ]
    }
    serialized = _event_text(event)
    for protected in (
        "+79991234567",
        "https://t.me/anna_guide",
        "https://max.ru/anna.guide",
        "https://vk.com/anna-guide",
    ):
        assert protected not in serialized

    no_op = auth_client.patch(
        "/api/v1/account",
        json={
            **payload,
            "version": payload["version"],
        },
    )
    assert no_op.status_code == 200
    assert db_session.scalar(
        select(func.count()).select_from(AuditEventORM).where(
            AuditEventORM.action == "account_profile_updated"
        )
    ) == 1


def test_profile_rejects_stale_version_and_untrusted_social_host(auth_client):
    _bootstrap(auth_client)
    first = auth_client.patch(
        "/api/v1/account",
        json=_profile_payload(version=1),
    )
    assert first.status_code == 200

    stale = auth_client.patch(
        "/api/v1/account",
        json={**_profile_payload(version=1), "display_name": "Устаревшее имя"},
    )
    assert stale.status_code == 409

    invalid = auth_client.patch(
        "/api/v1/account",
        json={
            **_profile_payload(version=first.json()["version"]),
            "telegram_url": "https://example.org/not-telegram",
        },
    )
    assert invalid.status_code == 422


def test_active_club_contacts_are_visible_and_vcard_is_downloadable(
    auth_client,
    db_session,
):
    current = _bootstrap(auth_client)
    active = UserORM(
        email="guide@example.org",
        display_name="Борис Инструктор",
        phone="+491234567890",
        telegram_url="https://t.me/boris_guide",
        max_url="https://max.ru/boris-guide",
        vk_url="https://vk.com/id12345",
        role="verified_instructor",
        password_hash=hash_password(MEMBER_SECRET),
        is_active=True,
    )
    inactive = UserORM(
        email="inactive@example.org",
        display_name="Неактивный Участник",
        role="instructor",
        password_hash=hash_password(MEMBER_SECRET),
        is_active=False,
    )
    db_session.add_all([active, inactive])
    db_session.commit()

    response = auth_client.get("/api/v1/account/contacts")
    assert response.status_code == 200
    contacts = response.json()
    assert [item["display_name"] for item in contacts] == [
        "Борис Инструктор",
        "Первый Администратор",
    ]
    assert all(item["display_name"] != "Неактивный Участник" for item in contacts)
    assert next(item for item in contacts if item["id"] == current["id"])["is_current"]
    guide = next(item for item in contacts if item["id"] == active.id)
    assert guide["email"] == "guide@example.org"
    assert guide["phone"] == "+491234567890"
    assert guide["telegram_url"] == "https://t.me/boris_guide"

    card = auth_client.get(f"/api/v1/account/contacts/{active.id}/vcard")
    assert card.status_code == 200
    assert card.headers["content-type"].startswith("text/vcard")
    assert f"tourhub-contact-{active.id}.vcf" in card.headers["content-disposition"]
    assert "BEGIN:VCARD\r\nVERSION:3.0" in card.text
    assert "FN:Борис Инструктор" in card.text
    assert "EMAIL;TYPE=INTERNET:guide@example.org" in card.text
    assert "TEL;TYPE=CELL:+491234567890" in card.text
    assert "URL;TYPE=Telegram:https://t.me/boris_guide" in card.text

    missing = auth_client.get(f"/api/v1/account/contacts/{inactive.id}/vcard")
    assert missing.status_code == 404


def test_password_change_preserves_current_session_and_revokes_other_sessions(
    auth_client,
    db_session,
):
    _bootstrap(auth_client)
    second_client = TestClient(app)
    second_login = second_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@tourhub.local", PASSWORD_FIELD: ADMIN_SECRET},
    )
    assert second_login.status_code == 200
    assert db_session.scalar(select(func.count()).select_from(AuthSessionORM)) == 2

    response = auth_client.post(
        "/api/v1/account/password",
        json={
            f"current_{PASSWORD_FIELD}": ADMIN_SECRET,
            f"new_{PASSWORD_FIELD}": NEW_SECRET,
            f"new_{PASSWORD_FIELD}_confirm": NEW_SECRET,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["version"] == 2
    assert auth_client.get("/api/v1/auth/me").status_code == 200
    assert second_client.get("/api/v1/auth/me").status_code == 401

    old_login = TestClient(app).post(
        "/api/v1/auth/login",
        json={"email": "admin@tourhub.local", PASSWORD_FIELD: ADMIN_SECRET},
    )
    assert old_login.status_code == 401
    new_login = TestClient(app).post(
        "/api/v1/auth/login",
        json={"email": "admin@tourhub.local", PASSWORD_FIELD: NEW_SECRET},
    )
    assert new_login.status_code == 200

    event = _event(db_session, "account_password_changed")
    assert event is not None
    assert event.before_data == {"version": 1}
    assert event.after_data == {"version": 2}
    assert event.context_data == {
        "current_session_preserved": True,
        "revoked_other_session_count": 1,
    }
    serialized = _event_text(event)
    assert ADMIN_SECRET not in serialized
    assert NEW_SECRET not in serialized
    stored_user = db_session.scalar(
        select(UserORM).where(UserORM.email == "admin@tourhub.local")
    )
    assert stored_user is not None
    assert stored_user.password_hash not in serialized


def test_password_change_rejects_wrong_current_password(auth_client):
    _bootstrap(auth_client)
    response = auth_client.post(
        "/api/v1/account/password",
        json={
            f"current_{PASSWORD_FIELD}": "-".join(("wrong", "phrase", "123456789")),
            f"new_{PASSWORD_FIELD}": NEW_SECRET,
            f"new_{PASSWORD_FIELD}_confirm": NEW_SECRET,
        },
    )
    assert response.status_code == 400
    assert auth_client.get("/api/v1/auth/me").status_code == 200


def test_profile_update_rolls_back_when_audit_fails(db_session, monkeypatch):
    actor = UserORM(
        id=1,
        email="member@example.org",
        display_name="Исходное Имя",
        role="instructor",
        password_hash=hash_password(MEMBER_SECRET),
        is_active=True,
    )
    db_session.add(actor)
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    request = AccountProfileUpdateRequest(
        display_name="Новое Имя",
        phone="+7 999 000 00 00",
        telegram_url="new_member",
        max_url=None,
        vk_url=None,
        version=1,
    )
    try:
        AccountProfileService(db_session, actor=actor).update_profile(request)
    except RuntimeError as error:
        assert str(error) == "audit failure"
    else:
        raise AssertionError("audit failure was not propagated")

    db_session.expire_all()
    stored = db_session.get(UserORM, actor.id)
    assert stored is not None
    assert stored.display_name == "Исходное Имя"
    assert stored.phone is None
    assert stored.version == 1
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
