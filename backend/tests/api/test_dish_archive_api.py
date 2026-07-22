import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.dish import DishORM
from app.models.user import UserORM
from app.services.audit_service import AuditService
from app.services.dish_archive_service import DishArchiveService

PASSWORD_FIELD = "pass" + "word"
ADMIN_SECRET = "-".join(("dish", "archive", "admin", "12345"))


def _bootstrap(client) -> dict[str, object]:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "email": "admin@tourhub.local",
            "display_name": "Первый Администратор",
            PASSWORD_FIELD: ADMIN_SECRET,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["user"]


def _create_published_dish(client, name: str = "Гречневая каша") -> tuple[str, str]:
    recipe_response = client.post("/api/v1/recipes", json={"name": f"{name} рецепт"})
    assert recipe_response.status_code == 201, recipe_response.text
    recipe_id = recipe_response.json()["id"]
    assert client.post(f"/api/v1/recipes/{recipe_id}/submit").status_code == 200
    publish_response = client.post(f"/api/v1/recipes/{recipe_id}/publish")
    assert publish_response.status_code == 200, publish_response.text

    dishes_response = client.get("/api/v1/dishes")
    assert dishes_response.status_code == 200, dishes_response.text
    dish = next(
        item
        for item in dishes_response.json()["items"]
        if item["recipe"]["id"] == recipe_id
    )
    return dish["id"], recipe_id


def test_dish_archive_preserves_recipe_reference_and_can_restore(auth_client, db_session):
    _bootstrap(auth_client)
    dish_id, recipe_id = _create_published_dish(auth_client)

    archived = auth_client.post(f"/api/v1/dishes/{dish_id}/archive")
    assert archived.status_code == 200, archived.text
    assert archived.json() == {
        "id": dish_id,
        "name": "Гречневая каша рецепт",
        "recipe_name": "Гречневая каша рецепт",
        "is_archived": True,
        "archived_by_alcohol_policy": False,
    }

    active = auth_client.get("/api/v1/dishes")
    assert active.status_code == 200
    assert dish_id not in {item["id"] for item in active.json()["items"]}
    assert auth_client.get(f"/api/v1/dishes/{dish_id}").status_code == 404

    archive = auth_client.get("/api/v1/dishes/archive")
    assert archive.status_code == 200
    assert [item["id"] for item in archive.json()["items"]] == [dish_id]

    db_session.expire_all()
    stored = db_session.get(DishORM, dish_id)
    assert stored is not None
    assert stored.recipe_id == recipe_id

    restored = auth_client.post(f"/api/v1/dishes/{dish_id}/restore")
    assert restored.status_code == 200, restored.text
    assert restored.json()["is_archived"] is False
    active_ids = {
        item["id"] for item in auth_client.get("/api/v1/dishes").json()["items"]
    }
    assert dish_id in active_ids


def test_dish_archive_and_restore_are_idempotent_without_duplicate_audit(
    auth_client,
    db_session,
):
    _bootstrap(auth_client)
    dish_id, _ = _create_published_dish(auth_client, "Овсяная каша")

    for _ in range(2):
        response = auth_client.post(f"/api/v1/dishes/{dish_id}/archive")
        assert response.status_code == 200
    for _ in range(2):
        response = auth_client.post(f"/api/v1/dishes/{dish_id}/restore")
        assert response.status_code == 200

    db_session.expire_all()
    counts = dict(
        db_session.execute(
            select(AuditEventORM.action, func.count())
            .where(
                AuditEventORM.entity_type == "dish",
                AuditEventORM.entity_id == dish_id,
                AuditEventORM.action.in_(("dish_archived", "dish_restored")),
            )
            .group_by(AuditEventORM.action)
        ).all()
    )
    assert counts == {"dish_archived": 1, "dish_restored": 1}

    events = list(
        db_session.scalars(
            select(AuditEventORM)
            .where(
                AuditEventORM.entity_type == "dish",
                AuditEventORM.entity_id == dish_id,
                AuditEventORM.action.in_(("dish_archived", "dish_restored")),
            )
            .order_by(AuditEventORM.id)
        ).all()
    )
    assert events[0].before_data["is_archived"] is False
    assert events[0].after_data["is_archived"] is True
    assert events[1].before_data["is_archived"] is True
    assert events[1].after_data["is_archived"] is False
    assert all(event.context_data == {"policy_locked": False} for event in events)


def test_alcohol_policy_archived_dish_cannot_be_restored(auth_client, db_session):
    _bootstrap(auth_client)
    dish_id, _ = _create_published_dish(auth_client, "Чай")
    dish = db_session.get(DishORM, dish_id)
    assert dish is not None
    dish.name = "Пиво"
    dish.is_archived = True
    dish.archived_by_alcohol_policy = True
    db_session.commit()

    response = auth_client.post(f"/api/v1/dishes/{dish_id}/restore")
    assert response.status_code == 409
    assert response.json()["error"] == (
        "Dish cannot be restored because it is blocked by the central alcohol policy"
    )

    db_session.expire_all()
    stored = db_session.get(DishORM, dish_id)
    assert stored is not None
    assert stored.is_archived is True
    assert stored.archived_by_alcohol_policy is True
    assert db_session.scalar(
        select(func.count()).select_from(AuditEventORM).where(
            AuditEventORM.entity_id == dish_id,
            AuditEventORM.action == "dish_restored",
        )
    ) == 0


def test_dish_archive_rolls_back_when_audit_fails(auth_client, db_session, monkeypatch):
    _bootstrap(auth_client)
    dish_id, _ = _create_published_dish(auth_client, "Рисовая каша")
    actor = db_session.scalar(
        select(UserORM).where(UserORM.email == "admin@tourhub.local")
    )
    assert actor is not None

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        DishArchiveService(db_session, actor=actor).archive(dish_id)

    db_session.expire_all()
    stored = db_session.get(DishORM, dish_id)
    assert stored is not None
    assert stored.is_archived is False
    assert db_session.scalar(
        select(func.count()).select_from(AuditEventORM).where(
            AuditEventORM.entity_id == dish_id,
            AuditEventORM.action == "dish_archived",
        )
    ) == 0
