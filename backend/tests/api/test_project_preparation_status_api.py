def test_project_preparation_status_starts_empty(client):
    created = client.post(
        "/api/v1/projects",
        json={
            "name": "Карелия",
            "participants": 8,
            "days": 3,
            "first_meal": "dinner",
            "last_meal": "breakfast",
        },
    )
    assert created.status_code == 200
    project_id = created.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}/preparation")

    assert response.status_code == 200
    assert response.json() == {
        "project_id": project_id,
        "meal_plan_id": "",
        "purchase_list_id": "",
        "purchase_checklist_id": "",
        "equipment_list_id": "",
    }


def test_project_preparation_status_requires_project(client):
    response = client.get("/api/v1/projects/999/preparation")

    assert response.status_code == 404
