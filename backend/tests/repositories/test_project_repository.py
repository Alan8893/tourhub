from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository


def test_project_repository_get_by_id(db_session):
    project = ProjectORM(
        id=1,
        name="Altai Trip 2026",
        participants=10,
        days=7,
        status="draft",
    )

    db_session.add(project)
    db_session.commit()

    repository = ProjectRepository(db_session)

    result = repository.get_by_id(project.id)

    assert result is not None
    assert result.name == project.name
    assert result.participants == project.participants
