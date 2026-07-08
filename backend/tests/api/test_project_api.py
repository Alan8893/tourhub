from app.models import ProjectORM


def test_get_project_endpoint(client, db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    db_session.add(project)
    db_session.commit()

    response = client.get("/api/v1/projects/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["name"] == "Altai Trip 2026"
    assert data["participants"] == 10
    assert data["days"] == 7
    assert data["status"] == "draft"
