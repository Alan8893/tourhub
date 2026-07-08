def test_get_project_endpoint(client):
    response = client.get("/api/v1/projects/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Altai Trip 2026"
    assert data["participants"] == 10
    assert data["days"] == 7
    assert data["status"] == "draft"
