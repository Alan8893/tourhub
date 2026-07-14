def test_list_projects_returns_all_projects_newest_first(client):
    first = client.post(
        "/api/v1/projects",
        json={"name": "Первый поход", "participants": 8, "days": 3},
    )
    second = client.post(
        "/api/v1/projects",
        json={"name": "Второй поход", "participants": 12, "days": 5},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["name"] for item in items] == ["Второй поход", "Первый поход"]
    assert items[0]["participants"] == 12
    assert items[1]["days"] == 3
