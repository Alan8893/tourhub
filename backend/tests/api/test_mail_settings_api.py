def _payload(settings: dict[str, object]) -> dict[str, object]:
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


def _validation_messages(response) -> str:
    body = response.json()
    assert body["error"] == "Validation Error"
    return " ".join(item["msg"] for item in body["details"])


def test_mail_settings_defaults_and_deferred_status(client, monkeypatch) -> None:
    monkeypatch.delenv("TOURHUB_SMTP_SECRET", raising=False)
    response = client.get("/api/v1/settings/mail")
    assert response.status_code == 200
    settings = response.json()

    assert settings["version"] == 1
    assert settings["smtp_host"] == "localhost"
    assert settings["smtp_port"] == 587
    assert settings["security_mode"] == "starttls"
    assert settings["smtp_username"] is None
    assert settings["sender_email"] == "tourhub@localhost"
    assert settings["sender_name"] == "TourHub"
    assert settings["reply_to_email"] is None
    assert settings["test_recipient_email"] is None
    assert settings["timeout_seconds"] == 30
    assert settings["retry_count"] == 3
    assert settings["secret_configured"] is False
    assert settings["secret_source"] == "environment"
    assert settings["secret_environment_variable"] == "TOURHUB_SMTP_SECRET"
    assert settings["delivery_available"] is False
    assert settings["test_delivery_available"] is False


def test_mail_secret_status_is_derived_without_echo(client, monkeypatch) -> None:
    marker = "configured-value-that-must-not-be-returned"
    monkeypatch.setenv("TOURHUB_SMTP_SECRET", marker)

    response = client.get("/api/v1/settings/mail")
    assert response.status_code == 200
    body = response.json()
    assert body["secret_configured"] is True
    assert marker not in str(body)


def test_mail_settings_persist_normalized_values_and_safe_history(client) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    payload = _payload(initial)
    payload.update(
        {
            "smtp_host": " SMTP.Example.COM. ",
            "smtp_port": 465,
            "security_mode": "tls",
            "smtp_username": " mailer ",
            "sender_email": "TourHub@Example.COM",
            "sender_name": " Турклуб ",
            "reply_to_email": "support@Example.COM",
            "test_recipient_email": "admin@Example.COM",
            "timeout_seconds": 45,
            "retry_count": 5,
        }
    )

    response = client.put("/api/v1/settings/mail", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["version"] == 2
    assert updated["smtp_host"] == "smtp.example.com"
    assert updated["smtp_port"] == 465
    assert updated["security_mode"] == "tls"
    assert updated["smtp_username"] == "mailer"
    assert updated["sender_email"] == "TourHub@example.com"
    assert updated["sender_name"] == "Турклуб"
    assert updated["reply_to_email"] == "support@example.com"
    assert updated["test_recipient_email"] == "admin@example.com"
    assert updated["timeout_seconds"] == 45
    assert updated["retry_count"] == 5
    assert updated["delivery_available"] is False

    history = client.get("/api/v1/settings/mail/history").json()
    assert len(history) == 1
    assert history[0]["settings_version"] == 2
    assert set(history[0]["changed_fields"]) == {
        "smtp_host",
        "smtp_port",
        "security_mode",
        "smtp_username",
        "sender_email",
        "sender_name",
        "reply_to_email",
        "test_recipient_email",
        "timeout_seconds",
        "retry_count",
    }
    assert "smtp.example.com" not in str(history[0])
    assert "admin@example.com" not in str(history[0])


def test_mail_settings_reject_unknown_credential_field(client) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    payload = _payload(initial)
    payload["credential_value"] = "must-not-be-accepted"

    response = client.put("/api/v1/settings/mail", json=payload)
    assert response.status_code == 422
    assert "Extra inputs are not permitted" in _validation_messages(response)
    assert client.get("/api/v1/settings/mail").json()["version"] == 1
    assert client.get("/api/v1/settings/mail/history").json() == []


def test_mail_settings_reject_invalid_values_without_partial_save(client) -> None:
    initial = client.get("/api/v1/settings/mail").json()

    invalid_cases = [
        ("smtp_host", "https://smtp.example.com", "без протокола"),
        ("smtp_host", "smtp.example.com:587", "отдельном поле"),
        ("smtp_port", 0, "greater than or equal to 1"),
        ("security_mode", "automatic", "plain"),
        ("sender_email", "not-an-email", "корректным email"),
        ("reply_to_email", "bad @example.com", "пробелы"),
        ("timeout_seconds", 121, "less than or equal to 120"),
        ("retry_count", 11, "less than or equal to 10"),
    ]

    for field_name, value, message in invalid_cases:
        payload = _payload(initial)
        payload[field_name] = value
        response = client.put("/api/v1/settings/mail", json=payload)
        assert response.status_code == 422
        assert message in _validation_messages(response)

    current = client.get("/api/v1/settings/mail").json()
    assert current["version"] == 1
    assert current["smtp_host"] == "localhost"
    assert client.get("/api/v1/settings/mail/history").json() == []


def test_mail_settings_reject_stale_update(client) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    first = _payload(initial)
    first["smtp_port"] = 2525
    assert client.put("/api/v1/settings/mail", json=first).status_code == 200

    stale = _payload(initial)
    stale["retry_count"] = 1
    response = client.put("/api/v1/settings/mail", json=stale)
    assert response.status_code == 409
    assert "stale" in response.json()["error"]

    current = client.get("/api/v1/settings/mail").json()
    assert current["version"] == 2
    assert current["smtp_port"] == 2525
    assert current["retry_count"] == 3


def test_mail_settings_noop_does_not_add_history(client) -> None:
    initial = client.get("/api/v1/settings/mail").json()
    response = client.put("/api/v1/settings/mail", json=_payload(initial))
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert client.get("/api/v1/settings/mail/history").json() == []
