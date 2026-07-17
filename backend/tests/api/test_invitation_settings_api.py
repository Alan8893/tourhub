def _payload(settings: dict[str, object]) -> dict[str, object]:
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


def test_invitation_settings_defaults(client) -> None:
    response = client.get("/api/v1/settings/invitations")
    assert response.status_code == 200
    settings = response.json()

    assert settings["version"] == 1
    assert settings["expires_after_days"] == 7
    assert settings["default_role"] == "instructor"
    assert settings["allowed_email_domains"] == []
    assert settings["allow_resend"] is True
    assert settings["active_invitation_limit"] == 100
    assert settings["administrators_only"] is True
    assert settings["require_email_confirmation"] is True


def test_invitation_settings_persist_normalized_domains_and_safe_history(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    payload = _payload(initial)
    payload.update(
        {
            "expires_after_days": 14,
            "default_role": "verified_instructor",
            "allowed_email_domains": [
                " Example.COM ",
                "example.com",
                "пример.рф",
            ],
            "allow_resend": False,
            "active_invitation_limit": 25,
            "require_email_confirmation": False,
        }
    )

    response = client.put("/api/v1/settings/invitations", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["version"] == 2
    assert updated["expires_after_days"] == 14
    assert updated["default_role"] == "verified_instructor"
    assert updated["allowed_email_domains"] == [
        "example.com",
        "xn--e1afmkfd.xn--p1ai",
    ]
    assert updated["allow_resend"] is False
    assert updated["active_invitation_limit"] == 25
    assert updated["administrators_only"] is True
    assert updated["require_email_confirmation"] is False

    reloaded = client.get("/api/v1/settings/invitations").json()
    assert reloaded["version"] == 2
    assert reloaded["allowed_email_domains"] == updated["allowed_email_domains"]

    history = client.get("/api/v1/settings/invitations/history").json()
    assert len(history) == 1
    assert history[0]["settings_version"] == 2
    assert set(history[0]["changed_fields"]) == {
        "expires_after_days",
        "default_role",
        "allowed_email_domains",
        "allow_resend",
        "active_invitation_limit",
        "require_email_confirmation",
    }
    assert "example.com" not in str(history[0])
    assert "verified_instructor" not in str(history[0])


def test_invitation_settings_reject_administrator_default_role(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    payload = _payload(initial)
    payload["default_role"] = "administrator"

    response = client.put("/api/v1/settings/invitations", json=payload)
    assert response.status_code == 422
    assert "default_role" in response.json()["error"]
    assert client.get("/api/v1/settings/invitations").json()["version"] == 1


def test_invitation_settings_reject_invalid_domain_without_partial_save(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    payload = _payload(initial)
    payload["allowed_email_domains"] = ["admin@example.com"]

    response = client.put("/api/v1/settings/invitations", json=payload)
    assert response.status_code == 422
    assert "без @" in response.json()["error"]

    current = client.get("/api/v1/settings/invitations").json()
    assert current["version"] == 1
    assert current["allowed_email_domains"] == []
    assert client.get("/api/v1/settings/invitations/history").json() == []


def test_invitation_settings_reject_disabling_administrator_only(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    payload = _payload(initial)
    payload["administrators_only"] = False

    response = client.put("/api/v1/settings/invitations", json=payload)
    assert response.status_code == 422
    assert "только администраторы" in response.json()["error"]
    assert client.get("/api/v1/settings/invitations").json()["administrators_only"] is True


def test_invitation_settings_reject_out_of_range_values(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    expiry_payload = _payload(initial)
    expiry_payload["expires_after_days"] = 91
    assert client.put("/api/v1/settings/invitations", json=expiry_payload).status_code == 422

    limit_payload = _payload(initial)
    limit_payload["active_invitation_limit"] = 0
    assert client.put("/api/v1/settings/invitations", json=limit_payload).status_code == 422
    assert client.get("/api/v1/settings/invitations").json()["version"] == 1


def test_invitation_settings_reject_stale_update(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    first = _payload(initial)
    first["expires_after_days"] = 10
    assert client.put("/api/v1/settings/invitations", json=first).status_code == 200

    stale = _payload(initial)
    stale["active_invitation_limit"] = 50
    response = client.put("/api/v1/settings/invitations", json=stale)
    assert response.status_code == 409
    assert "stale" in response.json()["error"]

    current = client.get("/api/v1/settings/invitations").json()
    assert current["version"] == 2
    assert current["expires_after_days"] == 10
    assert current["active_invitation_limit"] == 100


def test_invitation_settings_noop_does_not_add_history(client) -> None:
    initial = client.get("/api/v1/settings/invitations").json()
    response = client.put("/api/v1/settings/invitations", json=_payload(initial))
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert client.get("/api/v1/settings/invitations/history").json() == []
