from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.models.audit_event import AuditEventORM
from app.models.recipe import RecipeORM
from app.models.user import UserORM
from app.schemas.user_administration import UserAdministrationUpdateRequest
from app.services.audit_service import AuditService
from app.services.recipe_lifecycle_service import RecipeLifecycleService
from app.services.user_administration_service import UserAdministrationService
from tests.conftest import TestingSessionLocal


def _user(
    *,
    email: str,
    display_name: str,
    role: str,
    is_active: bool = True,
) -> UserORM:
    return UserORM(
        email=email,
        display_name=display_name,
        role=role,
        password_hash="not-used",
        is_active=is_active,
    )


def test_user_access_change_is_attributed_and_filterable(client):
    session = TestingSessionLocal()
    administrator = _user(
        email="audit-admin@example.test",
        display_name="Audit Administrator",
        role="administrator",
    )
    target = _user(
        email="instructor@example.test",
        display_name="Instructor",
        role="instructor",
    )
    session.add_all([administrator, target])
    session.commit()
    target_id = target.id
    target_version = target.version

    updated = UserAdministrationService(session, actor=administrator).update(
        target_id,
        UserAdministrationUpdateRequest(
            expected_version=target_version,
            role="verified_instructor",
            is_active=True,
        ),
    )
    assert updated.role == "verified_instructor"
    session.close()

    response = client.get(
        "/api/v1/audit/events",
        params={
            "actor_user_id": administrator.id,
            "entity_type": "user",
            "entity_id": str(target_id),
            "action": "user_role_changed",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    event = payload["items"][0]
    assert event["actor_display_name"] == "Audit Administrator"
    assert event["actor_email"] == "audit-admin@example.test"
    assert event["actor_role"] == "administrator"
    assert event["before_data"]["role"] == "instructor"
    assert event["after_data"]["role"] == "verified_instructor"
    assert event["context_data"]["changed_fields"] == ["role"]


def test_recipe_rejection_creates_immutable_moderation_history(db_session):
    owner = _user(
        email="owner@example.test",
        display_name="Recipe Owner",
        role="instructor",
    )
    reviewer = _user(
        email="reviewer@example.test",
        display_name="Recipe Reviewer",
        role="administrator",
    )
    db_session.add_all([owner, reviewer])
    db_session.flush()
    recipe = RecipeORM(
        id="audit-recipe",
        name="Audit recipe",
        scope="personal",
        owner_user_id=owner.id,
        lifecycle_status="submitted",
        submitted_by_user_id=owner.id,
        submitted_at=datetime.now(UTC),
    )
    db_session.add(recipe)
    db_session.commit()

    rejected = RecipeLifecycleService(db_session, actor=reviewer).reject(
        recipe.id,
        "  Требуется уточнить технологию.  ",
    )
    assert rejected.lifecycle_status == "rejected"

    event = db_session.scalar(
        select(AuditEventORM).where(AuditEventORM.entity_id == recipe.id)
    )
    assert event is not None
    assert event.action == "recipe_rejected"
    assert event.actor_user_id == reviewer.id
    assert event.before_data is not None
    assert event.after_data is not None
    assert event.before_data["lifecycle_status"] == "submitted"
    assert event.after_data["lifecycle_status"] == "rejected"
    assert event.after_data["review_comment"] == "Требуется уточнить технологию."

    event.action = "tampered"
    with pytest.raises(RuntimeError, match="Audit events are immutable"):
        db_session.commit()
    db_session.rollback()


def test_sensitive_keys_are_removed_from_audit_payload(db_session):
    actor = _user(
        email="safe@example.test",
        display_name="Safe Actor",
        role="administrator",
    )
    db_session.add(actor)
    db_session.flush()
    AuditService(db_session).record(
        actor=actor,
        action="safe_test",
        entity_type="test",
        entity_id="one",
        before={
            "password_hash": "must-not-be-stored",
            "profile": {
                "session_token": "must-not-be-stored",
                "display_name": "Visible",
            },
        },
        after={"api_secret": "must-not-be-stored", "status": "ok"},
    )
    db_session.commit()

    event = db_session.scalar(select(AuditEventORM))
    assert event is not None
    assert event.before_data == {"profile": {"display_name": "Visible"}}
    assert event.after_data == {"status": "ok"}
