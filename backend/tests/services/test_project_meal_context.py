from app.modules.projects.service import ProjectService


def test_project_contains_last_meal(db_session):
    from app.modules.projects.repositories.project_repository import ProjectRepository

    service = ProjectService(ProjectRepository(db_session))

    project = service.create_project(
        name="Test Trip",
        participants=5,
        days=3,
        first_meal="dinner",
        last_meal="lunch",
    )

    assert project.first_meal == "dinner"
    assert project.last_meal == "lunch"
