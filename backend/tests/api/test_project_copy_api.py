import pytest
from sqlalchemy import func, select

from app.core.auth import require_preparation_access
from app.main import app
from app.models.audit_event import AuditEventORM
from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.models.project_instructor import ProjectInstructorORM
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.audit_service import AuditService


def _user(user_id: int, role: str = "instructor") -> UserORM:
    return UserORM(
        id=user_id,
        email=f"copy{user_id}@example.org",
        display_name=f"Copy User {user_id}",
        role=role,
        password_hash="not-used",
        is_active=True,
    )


def _act_as(actor: UserORM) -> None:
    app.dependency_overrides[require_preparation_access] = lambda: actor


def _source_project(
    db_session,
    *,
    owner: UserORM,
    status: str = "completed",
    archived_dish: bool = False,
) -> tuple[ProjectORM, DishORM]:
    source = ProjectORM(
        id=901,
        name="Завершённый Кавказ",
        participants=10,
        days=2,
        start_date="2026-08-01",
        first_meal="breakfast",
        last_meal="dinner",
        recipe_generation_mode="club_only",
        status=status,
        owner_user_id=owner.id,
    )
    recipe = RecipeORM(
        id="copy-recipe",
        name="Гречка для копирования",
        scope="club",
        lifecycle_status="published",
    )
    dish = DishORM(
        id="copy-dish",
        name="Гречка",
        recipe_id=recipe.id,
        is_archived=archived_dish,
    )
    plan = MealPlanORM(
        id="copy-source-plan",
        project=source,
        name=source.name,
        participants=source.participants,
        days_count=source.days,
        warnings=[],
    )
    day = MealPlanDayORM(id="copy-source-day", meal_plan=plan, day_number=1)
    slot = MealSlotORM(
        id="copy-source-slot",
        day=day,
        meal_type="breakfast",
        order=0,
        is_manually_edited=True,
    )
    slot_dish = MealSlotDishORM(
        id="copy-source-slot-dish",
        slot=slot,
        dish=dish,
        recipe=recipe,
        order=0,
    )
    item = MealPlanItemORM(
        id="copy-source-item",
        day=day,
        dish=dish,
        recipe=recipe,
        meal_type="breakfast",
    )
    db_session.add_all([owner, source, recipe, dish, plan, day, slot, slot_dish, item])
    db_session.commit()
    return source, dish


def _request() -> dict[str, object]:
    return {
        "name": "Новый Кавказ",
        "participants": 16,
        "days": 3,
        "start_date": "2026-09-10",
        "first_meal": "breakfast",
        "last_meal": "lunch",
        "recipe_generation_mode": "club_only",
    }


def test_owner_copies_completed_project_into_new_draft(client, db_session) -> None:
    owner = _user(81)
    source, _ = _source_project(db_session, owner=owner)
    source_snapshot = (
        source.name,
        source.participants,
        source.days,
        source.status,
        source.owner_user_id,
    )
    _act_as(owner)

    response = client.post(f"/api/v1/projects/{source.id}/copy", json=_request())

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["copied_slot_count"] == 1
    assert payload["copied_assignment_count"] == 1
    assert payload["skipped_assignment_count"] == 0
    assert payload["warnings"] == []

    db_session.expire_all()
    source_after = db_session.get(ProjectORM, source.id)
    assert source_after is not None
    assert (
        source_after.name,
        source_after.participants,
        source_after.days,
        source_after.status,
        source_after.owner_user_id,
    ) == source_snapshot

    destination = db_session.get(ProjectORM, payload["project_id"])
    assert destination is not None
    assert destination.id != source.id
    assert destination.name == "Новый Кавказ"
    assert destination.participants == 16
    assert destination.days == 3
    assert destination.status == "draft"
    assert destination.owner_user_id == owner.id
    assert destination.instructor_links == []
    assert destination.purchase_lists == []
    assert destination.purchase_checklists == []

    plan = MealPlanRepository(db_session).get_with_details(payload["meal_plan_id"])
    assert plan is not None
    assert plan.project_id == destination.id
    assert plan.days_count == 3
    assert len(plan.days) == 3
    copied = [item for day in plan.days for slot in day.slots for item in slot.dishes]
    assert [(item.dish_id, item.recipe_id) for item in copied] == [
        ("copy-dish", "copy-recipe")
    ]
    assert db_session.scalar(select(func.count()).select_from(MealPlanItemORM)) == 2

    event = db_session.scalar(
        select(AuditEventORM).where(AuditEventORM.action == "project_copied")
    )
    assert event is not None
    assert event.entity_id == str(destination.id)
    assert event.context_data["source_project_id"] == source.id
    assert event.context_data["copied_assignment_count"] == 1


def test_additional_instructor_cannot_copy_completed_project(client, db_session) -> None:
    owner = _user(82)
    collaborator = _user(83, "verified_instructor")
    source, _ = _source_project(db_session, owner=owner)
    db_session.add(collaborator)
    db_session.flush()
    db_session.add(
        ProjectInstructorORM(
            project_id=source.id,
            user_id=collaborator.id,
            added_by_user_id=owner.id,
        )
    )
    db_session.commit()
    _act_as(collaborator)

    response = client.post(f"/api/v1/projects/{source.id}/copy", json=_request())

    assert response.status_code == 403
    assert db_session.scalar(select(func.count()).select_from(ProjectORM)) == 1


def test_copy_requires_completed_source(client, db_session) -> None:
    owner = _user(84)
    source, _ = _source_project(db_session, owner=owner, status="draft")
    _act_as(owner)

    response = client.post(f"/api/v1/projects/{source.id}/copy", json=_request())

    assert response.status_code == 409
    assert db_session.scalar(select(func.count()).select_from(ProjectORM)) == 1


def test_archived_dependency_is_skipped_with_bounded_warning(client, db_session) -> None:
    owner = _user(85)
    source, _ = _source_project(db_session, owner=owner, archived_dish=True)
    _act_as(owner)

    response = client.post(f"/api/v1/projects/{source.id}/copy", json=_request())

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["copied_assignment_count"] == 0
    assert payload["skipped_assignment_count"] == 1
    assert len(payload["warnings"]) == 1
    plan = MealPlanRepository(db_session).get_with_details(payload["meal_plan_id"])
    assert plan is not None
    assert [item for day in plan.days for slot in day.slots for item in slot.dishes] == []


def test_audit_failure_rolls_back_destination(client, db_session, monkeypatch) -> None:
    owner = _user(86)
    source, _ = _source_project(db_session, owner=owner)
    _act_as(owner)

    def fail_record(*_args, **_kwargs):
        raise RuntimeError("forced project-copy audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)

    with pytest.raises(RuntimeError, match="forced project-copy audit failure"):
        client.post(f"/api/v1/projects/{source.id}/copy", json=_request())

    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(ProjectORM)) == 1
    assert db_session.scalar(select(func.count()).select_from(MealPlanORM)) == 1
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
