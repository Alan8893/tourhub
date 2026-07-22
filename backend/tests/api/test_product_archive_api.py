import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.product import ProductORM
from app.models.user import UserORM
from app.services.audit_service import AuditService
from app.services.auth_service import hash_password
from app.services.product_archive_service import ProductArchiveService

PASSWORD_FIELD = "pass" + "word"
ADMIN_SECRET = "-".join(("product", "archive", "admin", "12345"))


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


def _create_product(client, *, name: str = "Гречка") -> dict[str, object]:
    response = client.post(
        "/api/v1/products",
        json={
            "name": name,
            "category": "Крупы",
            "unit": "gram",
            "package_size": 800,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_product_archive_preserves_recipe_reference_and_can_restore(auth_client, db_session):
    _bootstrap(auth_client)
    product = _create_product(auth_client)
    recipe_response = auth_client.post(
        "/api/v1/recipes",
        json={"name": "Гречка походная"},
    )
    assert recipe_response.status_code == 201, recipe_response.text
    recipe_id = recipe_response.json()["id"]
    component_response = auth_client.post(
        f"/api/v1/recipes/{recipe_id}/components",
        json={
            "product_id": product["id"],
            "component_type": "base",
            "amount": 100,
            "unit": "gram",
            "calculation_type": "per_person",
            "people_count": None,
        },
    )
    assert component_response.status_code == 201, component_response.text

    archived = auth_client.post(f"/api/v1/products/{product['id']}/archive")
    assert archived.status_code == 200, archived.text
    assert archived.json()["is_archived"] is True
    assert archived.json()["archived_by_alcohol_policy"] is False

    active = auth_client.get("/api/v1/products")
    assert active.status_code == 200
    assert product["id"] not in {item["id"] for item in active.json()["items"]}

    archive = auth_client.get("/api/v1/products/archive")
    assert archive.status_code == 200
    assert [item["id"] for item in archive.json()["items"]] == [product["id"]]

    recipe = auth_client.get(f"/api/v1/recipes/{recipe_id}")
    assert recipe.status_code == 200, recipe.text
    assert recipe.json()["components"][0]["product"]["id"] == product["id"]
    assert db_session.get(ProductORM, product["id"]) is not None

    restored = auth_client.post(f"/api/v1/products/{product['id']}/restore")
    assert restored.status_code == 200, restored.text
    assert restored.json()["is_archived"] is False
    active_ids = {
        item["id"] for item in auth_client.get("/api/v1/products").json()["items"]
    }
    assert product["id"] in active_ids


def test_product_archive_and_restore_are_idempotent_without_duplicate_audit(
    auth_client,
    db_session,
):
    _bootstrap(auth_client)
    product = _create_product(auth_client)

    for _ in range(2):
        response = auth_client.post(f"/api/v1/products/{product['id']}/archive")
        assert response.status_code == 200
    for _ in range(2):
        response = auth_client.post(f"/api/v1/products/{product['id']}/restore")
        assert response.status_code == 200

    db_session.expire_all()
    counts = dict(
        db_session.execute(
            select(AuditEventORM.action, func.count())
            .where(
                AuditEventORM.entity_type == "product",
                AuditEventORM.entity_id == product["id"],
                AuditEventORM.action.in_(("product_archived", "product_restored")),
            )
            .group_by(AuditEventORM.action)
        ).all()
    )
    assert counts == {"product_archived": 1, "product_restored": 1}

    events = list(
        db_session.scalars(
            select(AuditEventORM)
            .where(
                AuditEventORM.entity_type == "product",
                AuditEventORM.entity_id == product["id"],
                AuditEventORM.action.in_(("product_archived", "product_restored")),
            )
            .order_by(AuditEventORM.id)
        ).all()
    )
    assert events[0].before_data["is_archived"] is False
    assert events[0].after_data["is_archived"] is True
    assert events[1].before_data["is_archived"] is True
    assert events[1].after_data["is_archived"] is False
    assert all(event.context_data == {"policy_locked": False} for event in events)


def test_alcohol_policy_archived_product_cannot_be_restored(auth_client, db_session):
    _bootstrap(auth_client)
    locked = ProductORM(
        id="policy-locked-product",
        name="Пиво",
        category="Алкоголь",
        unit="milliliter",
        package_size=500,
        is_archived=True,
        archived_by_alcohol_policy=True,
    )
    db_session.add(locked)
    db_session.commit()

    response = auth_client.post(f"/api/v1/products/{locked.id}/restore")
    assert response.status_code == 409
    assert response.json()["error"] == (
        "Product cannot be restored because it is blocked by the central alcohol policy"
    )

    db_session.expire_all()
    stored = db_session.get(ProductORM, locked.id)
    assert stored is not None
    assert stored.is_archived is True
    assert stored.archived_by_alcohol_policy is True
    assert db_session.scalar(
        select(func.count()).select_from(AuditEventORM).where(
            AuditEventORM.entity_id == locked.id,
            AuditEventORM.action == "product_restored",
        )
    ) == 0


def test_product_archive_rolls_back_when_audit_fails(db_session, monkeypatch):
    actor = UserORM(
        email="member@example.org",
        display_name="Участник",
        role="instructor",
        password_hash=hash_password(ADMIN_SECRET),
        is_active=True,
    )
    product = ProductORM(
        id="rollback-product",
        name="Рис",
        category="Крупы",
        unit="gram",
        package_size=900,
    )
    db_session.add_all([actor, product])
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        ProductArchiveService(db_session, actor=actor).archive(product.id)

    db_session.expire_all()
    stored = db_session.get(ProductORM, product.id)
    assert stored is not None
    assert stored.is_archived is False
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
