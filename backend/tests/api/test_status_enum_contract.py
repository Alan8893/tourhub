def test_purchase_list_status_contract_uses_enum_values(client):
    response = client.get("/api/v1/purchase-lists/not-existing")

    assert response.status_code == 404


def test_purchase_checklist_status_contract_uses_enum_values(client):
    response = client.get("/api/v1/purchase-checklists/not-existing")

    assert response.status_code == 404


def test_openapi_contains_status_enum_contract(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "components" in schema
    assert "schemas" in schema["components"]
