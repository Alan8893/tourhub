import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.equipment_list import EquipmentListORM
from app.models.meal_plan import MealPlanORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_list import PurchaseListORM
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.modules.projects.service import ProjectService
from app.repositories.meal_plan_repository import MealPlanRepository
from app.repositories.purchase_checklist_repository import PurchaseChecklistRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.audit_service import AuditService
from app.services.meal_plan_shopping_service import MealPlanShoppingService
from app.services.project_participant_recalculation_service import (
    ProjectParticipantRecalculationService,
)
from app.services.project_preparation_service import ProjectPreparationService
from app.services.purchase_checklist_service import PurchaseChecklistService
from app.services.purchase_list_service import PurchaseListService
from app.services.shopping_list_service import ShoppingListService


def _actor() -> UserORM:
    return UserORM(
        id=1,
        email="admin@test.local",
        display_name="Test Administrator",
        role="administrator",
        password_hash="not-used",
        is_active=True,
    )


def _project_events(db_session, project_id: int) -> list[AuditEventORM]:
    db_session.expire_all()
    return list(
        db_session.scalars(
            select(AuditEventORM)
            .where(
                AuditEventORM.entity_type == "project",
                AuditEventORM.entity_id == str(project_id),
            )
            .order_by(AuditEventORM.id)
        ).all()
    )


def test_project_create_and_updates_are_attributed_and_noops_are_skipped(
    client,
    db_session,
):
    create_response = client.post(
        "/api/v1/projects",
        json={"name": "Аудируемый поход", "participants": 8, "days": 3},
    )
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    participants_response = client.patch(
        f"/api/v1/projects/{project_id}/participants",
        json={"participants": 12},
    )
    assert participants_response.status_code == 200
    assert client.patch(
        f"/api/v1/projects/{project_id}/participants",
        json={"participants": 12},
    ).status_code == 200

    mode_response = client.patch(
        f"/api/v1/projects/{project_id}/recipe-generation-mode",
        json={"recipe_generation_mode": "personal_preferred"},
    )
    assert mode_response.status_code == 200
    assert client.patch(
        f"/api/v1/projects/{project_id}/recipe-generation-mode",
        json={"recipe_generation_mode": "personal_preferred"},
    ).status_code == 200

    events = _project_events(db_session, project_id)
    assert [event.action for event in events] == [
        "project_created",
        "project_participants_updated",
        "project_generation_mode_updated",
    ]
    assert all(event.actor_user_id == 1 for event in events)
    assert all(event.actor_display_name == "Test Administrator" for event in events)
    assert all(event.actor_email == "admin@test.local" for event in events)
    assert all(event.actor_role == "administrator" for event in events)

    created, participants_updated, mode_updated = events
    assert created.before_data is None
    assert created.after_data["name"] == "Аудируемый поход"
    assert created.after_data["participants"] == 8
    assert participants_updated.before_data["participants"] == 8
    assert participants_updated.after_data["participants"] == 12
    assert participants_updated.context_data["changed_fields"] == ["participants"]
    assert mode_updated.before_data["recipe_generation_mode"] == "club_only"
    assert mode_updated.after_data["recipe_generation_mode"] == "personal_preferred"


def test_project_preparation_is_audited_in_the_preparation_commit(client, db_session):
    project = ProjectORM(
        id=41,
        name="Подготовка с аудитом",
        participants=6,
        days=1,
        status="draft",
    )
    meal_plan = MealPlanORM(
        id="audit-plan",
        project=project,
        name=project.name,
        participants=project.participants,
        days_count=project.days,
    )
    db_session.add_all([project, meal_plan])
    db_session.commit()

    response = client.post("/api/v1/projects/41/prepare")
    assert response.status_code == 200
    payload = response.json()

    events = _project_events(db_session, project.id)
    assert [event.action for event in events] == ["project_prepared"]
    event = events[0]
    assert event.before_data["purchase_list_count"] == 0
    assert event.before_data["purchase_checklist_count"] == 0
    assert event.after_data["purchase_list_count"] == 1
    assert event.after_data["purchase_checklist_count"] == 1
    assert event.after_data["equipment_list_id"] == payload["equipment_list_id"]
    assert event.context_data == {
        "meal_plan_id": "audit-plan",
        "purchase_list_id": payload["purchase_list_id"],
        "purchase_checklist_id": payload["purchase_checklist_id"],
        "equipment_list_id": payload["equipment_list_id"],
    }

    assert db_session.scalar(select(func.count()).select_from(PurchaseListORM)) == 1
    assert db_session.scalar(select(func.count()).select_from(PurchaseChecklistORM)) == 1
    assert db_session.scalar(select(func.count()).select_from(EquipmentListORM)) == 1


def test_project_creation_rolls_back_when_audit_recording_fails(
    db_session,
    monkeypatch,
):
    actor = _actor()
    db_session.add(actor)
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    service = ProjectService(ProjectRepository(db_session), actor=actor)

    with pytest.raises(RuntimeError, match="audit failure"):
        service.create_project("Не сохранится", participants=5, days=2)

    assert db_session.scalar(select(func.count()).select_from(ProjectORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0


def test_participant_update_rolls_back_when_audit_recording_fails(
    db_session,
    monkeypatch,
):
    actor = _actor()
    project = ProjectORM(
        id=52,
        name="Откат участников",
        participants=7,
        days=2,
        status="draft",
    )
    db_session.add_all([actor, project])
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    service = ProjectParticipantRecalculationService(
        db_session,
        MealPlanShoppingService(ShoppingListService(db_session)),
        actor=actor,
    )

    with pytest.raises(RuntimeError, match="audit failure"):
        service.update_participants(project.id, 15)

    db_session.expire_all()
    assert db_session.get(ProjectORM, project.id).participants == 7
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0


class _FailingEquipmentService:
    def create_from_meal_plan_id(
        self,
        meal_plan_id: str,
        project_id: int | None = None,
        *,
        commit: bool = True,
    ):
        raise RuntimeError("equipment failure")


def test_preparation_rolls_back_pending_lists_and_audit_on_failure(db_session):
    actor = _actor()
    project = ProjectORM(
        id=63,
        name="Откат подготовки",
        participants=4,
        days=1,
        status="draft",
    )
    meal_plan = MealPlanORM(
        id="rollback-plan",
        project=project,
        name=project.name,
        participants=project.participants,
        days_count=project.days,
    )
    db_session.add_all([actor, project, meal_plan])
    db_session.commit()
    db_session.refresh(project)

    meal_plan_repository = MealPlanRepository(db_session)
    shopping_service = MealPlanShoppingService(ShoppingListService(db_session))
    service = ProjectPreparationService(
        PurchaseListService(
            PurchaseListRepository(db_session),
            meal_plan_repository,
            shopping_service,
        ),
        PurchaseChecklistService(
            PurchaseChecklistRepository(db_session),
            meal_plan_repository,
            shopping_service,
        ),
        _FailingEquipmentService(),
        session=db_session,
        actor=actor,
    )

    with pytest.raises(RuntimeError, match="equipment failure"):
        service.prepare_project(project)

    assert db_session.scalar(select(func.count()).select_from(PurchaseListORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(PurchaseChecklistORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
