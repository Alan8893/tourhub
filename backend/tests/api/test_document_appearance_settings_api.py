def _update_payload(settings: dict[str, object]) -> dict[str, object]:
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


def test_document_appearance_defaults_persistence_and_history(client) -> None:
    response = client.get("/api/v1/settings/documents")
    assert response.status_code == 200
    initial = response.json()
    assert initial["version"] == 1
    assert initial["primary_color"] == "#1B5E20"
    assert initial["logo_source"] == "main_logo"
    assert initial["show_contacts"] is True
    assert initial["table_density"] == "comfortable"

    payload = _update_payload(initial)
    payload.update(
        {
            "primary_color": "#075985",
            "accent_color": "#0F766E",
            "heading_color": "#075985",
            "logo_source": "document_image",
            "show_contacts": False,
            "footer_text": "Турклуб Север · внутренний документ",
            "use_document_image_as_title_background": True,
            "table_density": "compact",
        }
    )
    response = client.put("/api/v1/settings/documents", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["version"] == 2
    assert updated["primary_color"] == "#075985"
    assert updated["logo_source"] == "document_image"
    assert updated["show_contacts"] is False
    assert updated["table_density"] == "compact"

    current = client.get("/api/v1/settings/documents").json()
    assert current["version"] == 2
    assert current["footer_text"] == "Турклуб Север · внутренний документ"

    history = client.get("/api/v1/settings/documents/history").json()
    assert len(history) == 1
    assert history[0]["actor_label"] == "Локальный администратор"
    assert history[0]["settings_version"] == 2
    assert "primary_color" in history[0]["changed_fields"]
    assert "footer_text" in history[0]["changed_fields"]
    assert "#075985" not in str(history[0])
    assert "внутренний документ" not in str(history[0])


def test_document_appearance_rejects_stale_update(client) -> None:
    initial = client.get("/api/v1/settings/documents").json()
    payload = _update_payload(initial)
    payload["table_density"] = "compact"
    assert client.put("/api/v1/settings/documents", json=payload).status_code == 200

    stale = _update_payload(initial)
    stale["logo_source"] = "none"
    response = client.put("/api/v1/settings/documents", json=stale)
    assert response.status_code == 409
    assert "stale" in response.json()["error"]

    current = client.get("/api/v1/settings/documents").json()
    assert current["version"] == 2
    assert current["table_density"] == "compact"
    assert current["logo_source"] == "main_logo"


def test_document_appearance_rejects_low_contrast_with_reason(client) -> None:
    initial = client.get("/api/v1/settings/documents").json()
    payload = _update_payload(initial)
    payload["table_header_text"] = payload["table_header_background"]

    response = client.put("/api/v1/settings/documents", json=payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert "контраст" in error
    assert "4.5:1" in error


def test_document_appearance_noop_does_not_add_history(client) -> None:
    initial = client.get("/api/v1/settings/documents").json()
    response = client.put(
        "/api/v1/settings/documents",
        json=_update_payload(initial),
    )
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert client.get("/api/v1/settings/documents/history").json() == []


def test_document_appearance_validates_typed_controls(client) -> None:
    initial = client.get("/api/v1/settings/documents").json()
    payload = _update_payload(initial)
    payload["primary_color"] = "green"
    assert client.put("/api/v1/settings/documents", json=payload).status_code == 422

    payload = _update_payload(initial)
    payload["logo_source"] = "remote_url"
    assert client.put("/api/v1/settings/documents", json=payload).status_code == 422

    payload = _update_payload(initial)
    payload["footer_text"] = "x" * 501
    assert client.put("/api/v1/settings/documents", json=payload).status_code == 422
