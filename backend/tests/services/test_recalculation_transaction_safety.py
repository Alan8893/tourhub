from types import SimpleNamespace

import pytest

from app.modules.api.meal_slot_router import _commit_recalculation
from app.services.project_participant_recalculation_service import (
    ProjectParticipantRecalculationService,
)


class RecordingSession:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.refreshed = []

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def refresh(self, value) -> None:
        self.refreshed.append(value)


class ProjectRepositoryStub:
    def __init__(self, project) -> None:
        self.project = project

    def get_by_id(self, project_id: int):
        return self.project if project_id == self.project.id else None


class MealPlanRepositoryStub:
    def __init__(self, meal_plan) -> None:
        self.meal_plan = meal_plan

    def get_by_project_id(self, project_id: int):
        return self.meal_plan

    def get_with_details(self, meal_plan_id: str):
        return self.meal_plan


class FailingPurchasingRefreshStub:
    def refresh(self, meal_plan) -> None:
        raise RuntimeError("recalculation failed")


def test_meal_slot_recalculation_rolls_back_failed_operation() -> None:
    session = RecordingSession()

    with pytest.raises(RuntimeError, match="recalculation failed"):
        _commit_recalculation(
            session,
            lambda: (_ for _ in ()).throw(RuntimeError("recalculation failed")),
        )

    assert session.commits == 0
    assert session.rollbacks == 1


def test_meal_slot_recalculation_commits_successful_operation() -> None:
    session = RecordingSession()

    result = _commit_recalculation(session, lambda: {"status": "ok"})

    assert result == {"status": "ok"}
    assert session.commits == 1
    assert session.rollbacks == 0


def test_participant_recalculation_rolls_back_when_refresh_fails() -> None:
    session = RecordingSession()
    project = SimpleNamespace(
        id=1,
        name="Rollback project",
        participants=10,
        days=2,
        recipe_generation_mode="club_only",
        status="draft",
    )
    meal_plan = SimpleNamespace(id="plan", participants=10)
    service = ProjectParticipantRecalculationService(session, SimpleNamespace())
    service.project_repository = ProjectRepositoryStub(project)
    service.meal_plan_repository = MealPlanRepositoryStub(meal_plan)
    service.purchasing_refresh_service = FailingPurchasingRefreshStub()

    with pytest.raises(RuntimeError, match="recalculation failed"):
        service.update_participants(project_id=1, participants=20)

    assert session.commits == 0
    assert session.rollbacks == 1
    assert session.refreshed == []
