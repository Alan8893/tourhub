import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.mail_settings import MailSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.mail_settings import MailDeliveryStatus
from app.services.audit_service import AuditService
from app.services.mail_delivery_service import (
    MailDeliveryFailedError,
    MailDeliveryResult,
    MailDeliveryService,
    MailDeliveryUnavailableError,
)
from app.services.mail_settings_service import MailSettingsService


def _events(db_session) -> list[AuditEventORM]:
    db_session.expire_all()
    return list(
        db_session.scalars(select(AuditEventORM).order_by(AuditEventORM.id)).all()
    )


def _club_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "club_name": settings["club_name"],
        "short_name": settings["short_name"],
        "legal_name": settings["legal_name"],
        "description": settings["description"],
        "address": settings["address"],
        "phone": settings["phone"],
        "email": settings["email"],
        "website": settings["website"],
        "timezone": settings["timezone"],
        "city": settings["city"],
        "region": settings["region"],
        "social_links": settings["social_links"],
        "images": {},
    }


def _appearance_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "preset_name": settings["preset_name"],
        "font_family": settings["font_family"],
        "density": settings["density"],
        "border_radius": settings["border_radius"],
        "button_style": settings["button_style"],
        "card_style": settings["card_style"],
        "shadows_enabled": settings["shadows_enabled"],
        "light": settings["light"],
        "dark": settings["dark"],
    }


def _document_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "primary_color": settings["primary_color"],
        "accent_color": settings["accent_color"],
        "heading_color": settings["heading_color"],
        "table_header_background": settings["table_header_background"],
        "table_header_text": settings["table_header_text"],
        "table_border_color": settings["table_border_color"],
        "title_background_color": settings["title_background_color"],
        "logo_source": settings["logo_source"],
        "show_contacts": settings["show_contacts"],
        "footer_text": settings["footer_text"],
        "use_document_image_as_title_background": settings[
            "use_document_image_as_title_background"
        ],
        "table_density": settings["table_density"],
    }


def _module_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "projects_visible": settings["projects_visible"],
        "catalogue_visible": settings["catalogue_visible"],
        "catalog_import_visible": settings["catalog_import_visible"],
        "shopping_visible": settings["shopping_visible"],
        "equipment_visible": settings["equipment_visible"],
        "documents_visible": settings["documents_visible"],
    }


def _invitation_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "expires_after_days": settings["expires_after_days"],
        "default_role": settings["default_role"],
        "allowed_email_domains": settings["allowed_email_domains"],
        "allow_resend": settings["allow_resend"],
        "active_invitation_limit": settings["active_invitation_limit"],
        "administrators_only": settings["administrators_only"],
        "require_email_confirmation": settings["require_email_confirmation"],
    }


def _mail_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "smtp_host": settings["smtp_host"],
        "smtp_port": settings["smtp_port"],
        "security_mode": settings["security_mode"],
        "smtp_username": settings["smtp_username"],
        "sender_email": settings["sender_email"],
        "sender_name": settings["sender_name"],
        "reply_to_email": settings["reply_to_email"],
        "test_recipient_email": settings["test_recipient_email"],
        "timeout_seconds": settings["timeout_seconds"],
        "retry_count": settings["retry_count"],
    }


def _assert_noop(client, path: str, payload: dict[str, object]) -> None:
    response = client.put(path, json=payload)
    assert response.status_code == 200


def test_all_typed_settings_writes_are_attributed_and_noops_are_skipped(
    client,
    db_session,
) -> None:
    club = client.get("/api/v1/settings/club").json()
    club_payload = _club_payload(club)
    club_payload["club_name"] = "Турклуб Аудит"
    club_updated = client.put("/api/v1/settings/club", json=club_payload)
    assert club_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/club",
        _club_payload(club_updated.json()),
    )

    appearance = client.get("/api/v1/settings/appearance").json()
    appearance_payload = _appearance_payload(appearance)
    appearance_payload["border_radius"] = appearance["border_radius"] + 1
    appearance_updated = client.put(
        "/api/v1/settings/appearance",
        json=appearance_payload,
    )
    assert appearance_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/appearance",
        _appearance_payload(appearance_updated.json()),
    )

    documents = client.get("/api/v1/settings/documents").json()
    document_payload = _document_payload(documents)
    document_payload["footer_text"] = "Безопасный футер"
    document_updated = client.put(
        "/api/v1/settings/documents",
        json=document_payload,
    )
    assert document_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/documents",
        _document_payload(document_updated.json()),
    )

    modules = client.get("/api/v1/settings/modules").json()
    module_payload = _module_payload(modules)
    module_payload["catalog_import_visible"] = False
    module_updated = client.put("/api/v1/settings/modules", json=module_payload)
    assert module_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/modules",
        _module_payload(module_updated.json()),
    )

    invitations = client.get("/api/v1/settings/invitations").json()
    invitation_payload = _invitation_payload(invitations)
    invitation_payload["expires_after_days"] = 8
    invitation_updated = client.put(
        "/api/v1/settings/invitations",
        json=invitation_payload,
    )
    assert invitation_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/invitations",
        _invitation_payload(invitation_updated.json()),
    )

    mail = client.get("/api/v1/settings/mail").json()
    mail_payload = _mail_payload(mail)
    mail_payload["smtp_port"] = 2525
    mail_updated = client.put("/api/v1/settings/mail", json=mail_payload)
    assert mail_updated.status_code == 200
    _assert_noop(
        client,
        "/api/v1/settings/mail",
        _mail_payload(mail_updated.json()),
    )

    events = _events(db_session)
    assert [(event.action, event.entity_type, event.entity_id) for event in events] == [
        ("club_settings_updated", "system_settings", "club"),
        ("appearance_settings_updated", "system_settings", "appearance"),
        (
            "document_appearance_settings_updated",
            "system_settings",
            "documents",
        ),
        ("module_settings_updated", "system_settings", "modules"),
        ("invitation_settings_updated", "system_settings", "invitations"),
        ("mail_settings_updated", "system_settings", "mail"),
    ]
    assert all(event.actor_user_id == 1 for event in events)
    assert all(event.actor_display_name == "Test Administrator" for event in events)
    assert all(event.actor_email == "admin@test.local" for event in events)
    assert all(event.actor_role == "administrator" for event in events)

    expected_changes = [
        "club_name",
        "border_radius",
        "footer_text",
        "catalog_import_visible",
        "expires_after_days",
        "smtp_port",
    ]
    for event, changed_field in zip(events, expected_changes, strict=True):
        assert event.before_data["version"] == 1
        assert event.after_data["version"] == 2
        assert event.before_data[changed_field] != event.after_data[changed_field]
        assert event.context_data["changed_fields"] == [changed_field]
        assert event.context_data["previous_version"] == 1
        assert event.context_data["settings_version"] == 2


def test_legacy_club_settings_write_uses_the_same_semantic_boundary(
    client,
    db_session,
) -> None:
    response = client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Legacy Club",
            "logo_data_url": None,
            "remove_logo": False,
        },
    )
    assert response.status_code == 200
    assert client.put(
        "/api/v1/club-settings",
        json={
            "club_name": "Legacy Club",
            "logo_data_url": None,
            "remove_logo": False,
        },
    ).status_code == 200

    events = _events(db_session)
    assert len(events) == 1
    event = events[0]
    assert event.action == "club_settings_updated"
    assert event.entity_type == "system_settings"
    assert event.entity_id == "club"
    assert event.context_data["changed_fields"] == ["club_name"]


def test_mail_settings_and_image_audit_never_store_protected_values(
    client,
    db_session,
    monkeypatch,
) -> None:
    secret = "smtp-password-that-must-never-be-audited"
    monkeypatch.setenv("TOURHUB_SMTP_SECRET", secret)

    mail = client.get("/api/v1/settings/mail").json()
    mail_payload = _mail_payload(mail)
    mail_payload["smtp_username"] = "mailer"
    assert client.put("/api/v1/settings/mail", json=mail_payload).status_code == 200

    club = client.get("/api/v1/settings/club").json()
    club_payload = _club_payload(club)
    club_payload["images"] = {
        "main_logo": {
            "data_url": (
                "data:image/png;base64,"
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
                "+A8AAQUBAScY42YAAAAASUVORK5CYII="
            ),
            "remove": False,
        }
    }
    assert client.put("/api/v1/settings/club", json=club_payload).status_code == 200

    serialized = str(
        [
            {
                "before": event.before_data,
                "after": event.after_data,
                "context": event.context_data,
            }
            for event in _events(db_session)
        ]
    )
    assert secret not in serialized
    assert "data:image" not in serialized
    assert "iVBOR" not in serialized
    assert "password" not in serialized.casefold()
    assert "token" not in serialized.casefold()

    club_event = _events(db_session)[-1]
    image_after = club_event.after_data["images.main_logo"]
    assert image_after["configured"] is True
    assert image_after["mime_type"] == "image/png"
    assert image_after["size_bytes"] > 0


def test_mail_operation_success_and_failure_outcomes_are_safe_and_attributed(
    client,
    db_session,
    monkeypatch,
) -> None:
    secret = "external-secret-not-for-audit"
    monkeypatch.setenv("TOURHUB_SMTP_SECRET", secret)

    def successful_check(_: MailDeliveryService) -> MailDeliveryResult:
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Соединение проверено.",
            attempts=1,
        )

    def successful_test(_: MailDeliveryService) -> MailDeliveryResult:
        return MailDeliveryResult(
            status=MailDeliveryStatus.SENT,
            message="Тест отправлен.",
            attempts=2,
            recipient="admin@example.org",
        )

    monkeypatch.setattr(MailDeliveryService, "check_connection", successful_check)
    monkeypatch.setattr(MailDeliveryService, "send_test_message", successful_test)
    assert client.post("/api/v1/settings/mail/check").status_code == 200
    assert client.post("/api/v1/settings/mail/test").status_code == 200

    def failed_check(_: MailDeliveryService) -> MailDeliveryResult:
        raise MailDeliveryFailedError("SMTP-операция не выполнена.", attempts=3)

    def unavailable_test(_: MailDeliveryService) -> MailDeliveryResult:
        raise MailDeliveryUnavailableError("Тестовая отправка недоступна.")

    monkeypatch.setattr(MailDeliveryService, "check_connection", failed_check)
    monkeypatch.setattr(MailDeliveryService, "send_test_message", unavailable_test)
    assert client.post("/api/v1/settings/mail/check").status_code == 502
    assert client.post("/api/v1/settings/mail/test").status_code == 409

    events = _events(db_session)
    assert [event.action for event in events] == [
        "mail_connection_checked",
        "mail_test_message_delivery",
        "mail_connection_checked",
        "mail_test_message_delivery",
    ]
    assert [event.after_data["status"] for event in events] == [
        "sent",
        "sent",
        "failed",
        "unavailable",
    ]
    assert [event.after_data["attempts"] for event in events] == [1, 2, 3, 0]
    assert events[1].after_data["recipient"] == "admin@example.org"
    assert all(event.entity_type == "mail" for event in events)
    assert all(event.entity_id == "smtp" for event in events)
    assert all(event.actor_user_id == 1 for event in events)
    assert secret not in str(events)
    assert all("smtp_host" not in event.context_data for event in events)


def test_settings_and_pending_audit_roll_back_when_the_owning_write_fails(
    client,
    db_session,
    monkeypatch,
) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    payload = _mail_payload(initial)
    payload["smtp_port"] = 2525

    def fail_after_flush(_: MailSettingsService) -> None:
        raise RuntimeError("history trim failure")

    monkeypatch.setattr(MailSettingsService, "_trim_history", fail_after_flush)
    with pytest.raises(RuntimeError, match="history trim failure"):
        client.put("/api/v1/settings/mail", json=payload)

    db_session.expire_all()
    settings = db_session.get(MailSettingsORM, 1)
    assert settings is not None
    assert settings.version == 1
    assert settings.smtp_port == 587
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
    assert (
        db_session.scalar(select(func.count()).select_from(SystemSettingsHistoryORM))
        == 0
    )


def test_settings_update_does_not_persist_when_audit_recording_fails(
    client,
    db_session,
    monkeypatch,
) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    payload = _mail_payload(initial)
    payload["smtp_port"] = 2525

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        client.put("/api/v1/settings/mail", json=payload)

    db_session.expire_all()
    settings = db_session.get(MailSettingsORM, 1)
    assert settings is not None
    assert settings.version == 1
    assert settings.smtp_port == 587
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
