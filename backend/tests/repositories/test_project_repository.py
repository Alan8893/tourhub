from app.modules.projects.repositories.project_repository import ProjectRepository


def test_project_repository_get_by_id(db_session, project):
    repository = ProjectRepository(db_session)

    result = repository.get_by_id(project.id)

    assert result is not None
    assert result.name == project.name
    assert result.participants == project.participants
