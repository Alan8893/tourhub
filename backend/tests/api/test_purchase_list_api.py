def test_purchase_list_router_registered(client):
    response = client.get(
        "/api/v1/purchase-lists/not-existing"
    )

    assert response.status_code in (404, 422)


def test_purchase_list_endpoint_exists(client):
    response = client.get(
        "/api/v1/purchase-lists/not-existing"
    )

    assert response.status_code != 405
