def test_openapi_contains_api_metadata(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "TourHub"
    assert schema["info"]["version"] == "0.1.0"


def test_openapi_contains_versioned_api_paths(client):
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert "/api/v1/meta" in paths
    assert any(path.startswith("/api/v1/") for path in paths)


def test_openapi_contains_meal_slot_editing_paths(client):
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert "/api/v1/meal-slots/{slot_id}/dishes/{dish_id}" in paths
    assert "/api/v1/meal-slots/{slot_id}/dishes/{slot_dish_id}" in paths
    assert (
        "/api/v1/meal-slots/{slot_id}/dishes/{slot_dish_id}/{dish_id}"
        in paths
    )


def test_openapi_does_not_expose_standalone_meal_plan_placeholder(client):
    response = client.get("/openapi.json")
    paths = response.json()["paths"]

    assert "/api/v1/meal-plans/generate" not in paths
    assert "/api/v1/meal-plans/" not in paths
