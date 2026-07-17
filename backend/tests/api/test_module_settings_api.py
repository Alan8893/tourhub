def _payload(settings: dict[str, object]) -> dict[str, object]:
    return {
        "expected_version": settings["version"],
        "projects_visible": settings["projects_visible"],
        "catalogue_visible": settings["catalogue_visible"],
        "catalog_import_visible": settings["catalog_import_visible"],
        "shopping_visible": settings["shopping_visible"],
        "equipment_visible": settings["equipment_visible"],
        "documents_visible": settings["documents_visible"],
    }


def test_module_settings_defaults_and_metadata(client) -> None:
    response = client.get("/api/v1/settings/modules")
    assert response.status_code == 200
    settings = response.json()

    assert settings["version"] == 1
    assert settings["projects_visible"] is True
    assert settings["catalogue_visible"] is True
    assert settings["catalog_import_visible"] is True
    assert settings["shopping_visible"] is True
    assert settings["equipment_visible"] is True
    assert settings["documents_visible"] is True

    definitions = {item["key"]: item for item in settings["modules"]}
    assert definitions["projects"]["required"] is True
    assert definitions["projects"]["locked"] is True
    assert "обязателен" in definitions["projects"]["lock_reason"]
    assert definitions["catalogue"]["required"] is True
    assert definitions["shopping"]["locked"] is True
    assert "Документы" in definitions["shopping"]["lock_reason"]
    assert definitions["equipment"]["locked"] is True
    assert definitions["documents"]["dependencies"] == ["shopping", "equipment"]


def test_module_settings_persist_visibility_and_safe_history(client) -> None:
    initial = client.get("/api/v1/settings/modules").json()
    payload = _payload(initial)
    payload.update(
        {
            "catalog_import_visible": False,
            "shopping_visible": False,
            "equipment_visible": False,
            "documents_visible": False,
        }
    )

    response = client.put("/api/v1/settings/modules", json=payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["version"] == 2
    assert updated["catalog_import_visible"] is False
    assert updated["shopping_visible"] is False
    assert updated["equipment_visible"] is False
    assert updated["documents_visible"] is False

    definitions = {item["key"]: item for item in updated["modules"]}
    assert definitions["shopping"]["locked"] is False
    assert definitions["equipment"]["locked"] is False

    reloaded = client.get("/api/v1/settings/modules").json()
    assert reloaded["version"] == 2
    assert reloaded["documents_visible"] is False

    history = client.get("/api/v1/settings/modules/history").json()
    assert len(history) == 1
    assert history[0]["settings_version"] == 2
    assert set(history[0]["changed_fields"]) == {
        "catalog_import_visible",
        "shopping_visible",
        "equipment_visible",
        "documents_visible",
    }
    assert "False" not in str(history[0])


def test_module_settings_reject_required_module_without_partial_save(client) -> None:
    initial = client.get("/api/v1/settings/modules").json()
    payload = _payload(initial)
    payload["projects_visible"] = False

    response = client.put("/api/v1/settings/modules", json=payload)
    assert response.status_code == 400
    assert "Проекты" in response.json()["error"]
    assert "обязателен" in response.json()["error"]

    current = client.get("/api/v1/settings/modules").json()
    assert current["version"] == 1
    assert current["projects_visible"] is True


def test_module_settings_reject_document_dependency_without_partial_save(client) -> None:
    initial = client.get("/api/v1/settings/modules").json()
    payload = _payload(initial)
    payload["shopping_visible"] = False

    response = client.put("/api/v1/settings/modules", json=payload)
    assert response.status_code == 400
    assert "Документы" in response.json()["error"]
    assert "Закупка" in response.json()["error"]

    current = client.get("/api/v1/settings/modules").json()
    assert current["version"] == 1
    assert current["shopping_visible"] is True
    assert current["documents_visible"] is True
    assert client.get("/api/v1/settings/modules/history").json() == []


def test_module_settings_reject_stale_update(client) -> None:
    initial = client.get("/api/v1/settings/modules").json()
    first = _payload(initial)
    first["catalog_import_visible"] = False
    assert client.put("/api/v1/settings/modules", json=first).status_code == 200

    stale = _payload(initial)
    stale["documents_visible"] = False
    response = client.put("/api/v1/settings/modules", json=stale)
    assert response.status_code == 409
    assert "stale" in response.json()["error"]

    current = client.get("/api/v1/settings/modules").json()
    assert current["version"] == 2
    assert current["catalog_import_visible"] is False
    assert current["documents_visible"] is True


def test_module_settings_noop_does_not_add_history(client) -> None:
    initial = client.get("/api/v1/settings/modules").json()
    response = client.put("/api/v1/settings/modules", json=_payload(initial))
    assert response.status_code == 200
    assert response.json()["version"] == 1
    assert client.get("/api/v1/settings/modules/history").json() == []
