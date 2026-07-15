import pytest

from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.service import ProjectService


def test_project_contains_last_meal(db_session):
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


def test_project_rejects_unknown_meal_type(db_session):
    service = ProjectService(ProjectRepository(db_session))

    with pytest.raises(ValueError, match="invalid start meal"):
        service.create_project(
            name="Invalid Trip",
            participants=5,
            days=2,
            first_meal="brunch",
            last_meal="dinner",
        )


def test_project_rejects_reversed_one_day_boundaries(db_session):
    service = ProjectService(ProjectRepository(db_session))

    with pytest.raises(ValueError, match="cannot finish before"):
        service.create_project(
            name="Invalid Day Trip",
            participants=5,
            days=1,
            first_meal="dinner",
            last_meal="breakfast",
        )


def test_project_requires_both_meal_boundaries(db_session):
    service = ProjectService(ProjectRepository(db_session))

    with pytest.raises(ValueError, match="provided together"):
        service.create_project(
            name="Incomplete Trip",
            participants=5,
            days=2,
            first_meal="breakfast",
        )
