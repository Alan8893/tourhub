def test_get_purchase_checklist_not_found(client):
    response = client.get(
        "/purchase-checklists/not-existing"
    )

    assert response.status_code in (404, 422)


def test_purchase_checklist_router_registered(client):
    response = client.get(
        "/purchase-checklists/not-existing"
    )

    assert response.status_code != 404 or response.json()
