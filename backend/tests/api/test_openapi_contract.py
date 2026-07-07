def test_openapi_contains_api_metadata(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == "TourHub"
    assert schema["info"]["version"] == "0.1.0"


def test_openapi_contains_versioned_api_paths(client):
    response = client.get("/openapi.json")

    schema = response.json()

    paths = schema["paths"]

    assert "/api/v1/meta" in paths
    assert any(path.startswith("/api/v1/") for path in paths)
