from copy import deepcopy


def _update_payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "preset_name": settings["preset_name"],
        "font_family": settings["font_family"],
        "density": settings["density"],
        "border_radius": settings["border_radius"],
        "button_style": settings["button_style"],
        "card_style": settings["card_style"],
        "shadows_enabled": settings["shadows_enabled"],
        "light": deepcopy(settings["light"]),
        "dark": deepcopy(settings["dark"]),
    }


def test_appearance_settings_defaults_presets_and_persistence(client) -> None:
    response = client.get("/api/v1/settings/appearance")
    assert response.status_code == 200
    initial = response.json()
    assert initial["version"] == 1
    assert initial["preset_name"] == "tourhub"
    assert initial["light"]["primary"] == "#1B5E20"
    assert initial["dark"]["background"] == "#101713"

    response = client.get("/api/v1/settings/appearance/presets")
    assert response.status_code == 200
    presets = response.json()
    assert [item["preset_name"] for item in presets] == [
        "tourhub",
        "forest",
        "ocean",
        "sunset",
    ]
    assert all(item["label"] for item in presets)

    payload = _update_payload(initial)
    payload.update(
        {
            "preset_name": "custom",
            "font_family": "humanist",
            "density": "compact",
            "border_radius": 16,
            "button_style": "soft",
            "card_style": "elevated",
            "shadows_enabled": False,
        }
    )
    payload["light"]["primary"] = "#245B35"

    response = client.put("/api/v1/settings/appearance", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["version"] == 2
    assert updated["preset_name"] == "custom"
    assert updated["font_family"] == "humanist"
    assert updated["density"] == "compact"
    assert updated["border_radius"] == 16
    assert updated["light"]["primary"] == "#245B35"

    response = client.get("/api/v1/settings/appearance")
    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert response.json()["light"]["primary"] == "#245B35"

    response = client.get("/api/v1/settings/appearance/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["actor_label"] == "Локальный администратор"
    assert history[0]["settings_version"] == 2
    assert "font_family" in history[0]["changed_fields"]
    assert "light.primary" in history[0]["changed_fields"]
    assert "#245B35" not in str(history[0])


def test_appearance_settings_reject_stale_update_without_overwrite(client) -> None:
    initial = client.get("/api/v1/settings/appearance").json()
    payload = _update_payload(initial)
    payload["border_radius"] = 12
    response = client.put("/api/v1/settings/appearance", json=payload)
    assert response.status_code == 200

    stale = _update_payload(initial)
    stale["border_radius"] = 20
    response = client.put("/api/v1/settings/appearance", json=stale)
    assert response.status_code == 409
    assert "stale" in response.json()["error"]

    current = client.get("/api/v1/settings/appearance").json()
    assert current["version"] == 2
    assert current["border_radius"] == 12


def test_appearance_settings_reject_low_contrast_with_reason(client) -> None:
    initial = client.get("/api/v1/settings/appearance").json()
    payload = _update_payload(initial)
    payload["light"]["text_primary"] = payload["light"]["background"]

    response = client.put("/api/v1/settings/appearance", json=payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert "Светлая тема" in error
    assert "контраст" in error
    assert "4.5:1" in error


def test_appearance_settings_noop_does_not_add_history(client) -> None:
    initial = client.get("/api/v1/settings/appearance").json()
    response = client.put(
        "/api/v1/settings/appearance",
        json=_update_payload(initial),
    )
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert client.get("/api/v1/settings/appearance/history").json() == []


def test_appearance_settings_validate_typed_controls(client) -> None:
    initial = client.get("/api/v1/settings/appearance").json()
    payload = _update_payload(initial)
    payload["border_radius"] = 25
    response = client.put("/api/v1/settings/appearance", json=payload)
    assert response.status_code == 422

    payload = _update_payload(initial)
    payload["light"]["primary"] = "green"
    response = client.put("/api/v1/settings/appearance", json=payload)
    assert response.status_code == 422
