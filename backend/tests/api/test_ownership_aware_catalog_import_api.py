import pytest
from sqlalchemy import select

from app.models.audit_event import AuditEventORM
from app.models.recipe import RecipeORM
from app.services.operational_audit_service import OperationalAuditService

PRODUCTS_CSV = """name;category;unit;package_size
Гречка;Крупы;gram;800
"""
RECIPES_CSV = """recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority
Походная гречка;Гречка;base;80;gram;per_person;;cooking_tip;Промыть крупу;10
"""


def _seed_product(client) -> None:
    response = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "products", "content": PRODUCTS_CSV},
    )
    assert response.status_code == 200, response.text
    assert response.json()["valid"] is True


def _preview(client, scope: str, content: str = RECIPES_CSV) -> dict[str, object]:
    response = client.post(
        "/api/v1/catalog-import/preview",
        json={
            "kind": "recipes",
            "content": content,
            "ownership_scope": scope,
        },
    )
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["valid"] is True
    assert result["ownership_scope"] == scope
    assert isinstance(result["preview_token"], str)
    assert len(result["preview_token"]) == 64
    return result


def _apply(client, scope: str, preview: dict[str, object], content: str = RECIPES_CSV):
    return client.post(
        "/api/v1/catalog-import/apply",
        json={
            "kind": "recipes",
            "content": content,
            "ownership_scope": scope,
            "preview_token": preview["preview_token"],
        },
    )


def test_personal_recipe_import_creates_owned_draft(client, db_session) -> None:
    _seed_product(client)
    preview = _preview(client, "personal")

    response = _apply(client, "personal", preview)

    assert response.status_code == 200, response.text
    assert response.json()["ownership_scope"] == "personal"
    db_session.expire_all()
    recipe = db_session.scalar(select(RecipeORM).where(RecipeORM.name == "Походная гречка"))
    assert recipe is not None
    assert recipe.scope == "personal"
    assert recipe.owner_user_id == 1
    assert recipe.lifecycle_status == "draft"

    item = next(
        item
        for item in client.get("/api/v1/recipes").json()["items"]
        if item["id"] == recipe.id
    )
    assert item["scope"] == "personal"
    assert item["owner_user_id"] == 1
    assert item["lifecycle_status"] == "draft"


def test_club_recipe_import_creates_published_recipe(client, db_session) -> None:
    _seed_product(client)
    preview = _preview(client, "club")

    response = _apply(client, "club", preview)

    assert response.status_code == 200, response.text
    db_session.expire_all()
    recipe = db_session.scalar(select(RecipeORM).where(RecipeORM.name == "Походная гречка"))
    assert recipe is not None
    assert recipe.scope == "club"
    assert recipe.owner_user_id is None
    assert recipe.lifecycle_status == "published"


def test_recipe_apply_rejects_scope_mismatch_without_writes_or_audit(
    client,
    db_session,
) -> None:
    _seed_product(client)
    preview = _preview(client, "personal")

    response = _apply(client, "club", preview)

    assert response.status_code == 409, response.text
    assert "изменились после проверки" in response.json()["error"]
    db_session.expire_all()
    assert db_session.scalar(select(RecipeORM)) is None
    import_events = list(
        db_session.scalars(
            select(AuditEventORM).where(
                AuditEventORM.action == "catalog_import_applied",
                AuditEventORM.entity_id == "recipes",
            )
        ).all()
    )
    assert import_events == []


def test_recipe_apply_rejects_changed_content_after_preview(client, db_session) -> None:
    _seed_product(client)
    preview = _preview(client, "personal")
    changed_content = RECIPES_CSV.replace("Походная гречка", "Другая гречка")

    response = _apply(client, "personal", preview, changed_content)

    assert response.status_code == 409, response.text
    db_session.expire_all()
    assert db_session.scalar(select(RecipeORM)) is None


def test_product_import_rejects_recipe_ownership_field(client) -> None:
    response = client.post(
        "/api/v1/catalog-import/preview",
        json={
            "kind": "products",
            "content": PRODUCTS_CSV,
            "ownership_scope": "personal",
        },
    )

    assert response.status_code == 422


def test_legacy_recipe_apply_without_scope_remains_club_import(client, db_session) -> None:
    _seed_product(client)

    response = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "recipes", "content": RECIPES_CSV},
    )

    assert response.status_code == 200, response.text
    db_session.expire_all()
    recipe = db_session.scalar(select(RecipeORM).where(RecipeORM.name == "Походная гречка"))
    assert recipe is not None
    assert recipe.scope == "club"
    assert recipe.owner_user_id is None
    assert recipe.lifecycle_status == "published"


def test_import_audit_failure_rolls_back_personal_recipe(
    client,
    db_session,
    monkeypatch,
) -> None:
    _seed_product(client)
    preview = _preview(client, "personal")

    def fail_audit(*args, **kwargs) -> None:
        raise RuntimeError("forced audit failure")

    monkeypatch.setattr(OperationalAuditService, "record_catalog_import", fail_audit)

    with pytest.raises(RuntimeError, match="forced audit failure"):
        _apply(client, "personal", preview)

    db_session.expire_all()
    assert db_session.scalar(select(RecipeORM)) is None
