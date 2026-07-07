

def test_purchase_list_not_found_error_contract(client):
    response = client.get("/purchase-lists/not-existing-id")

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data or "error" in data


def test_purchase_checklist_not_found_error_contract(client):
    response = client.get("/purchase-checklists/not-existing-id")

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data or "error" in data


def test_validation_error_contract(client):
    response = client.patch(
        "/purchase-checklists/items/test",
        json={"purchased_quantity": "invalid"},
    )

    assert response.status_code == 422

    data = response.json()

    assert "detail" in data or "error" in data
