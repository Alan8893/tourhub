def test_update_purchase_checklist_item_not_found(client):
    response = client.patch(
        "/api/v1/purchase-checklists/items/not-existing",
        json={
            "is_checked": True,
        },
    )

    assert response.status_code in (404, 422)
