from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.models.audit_event import AuditEventORM
from app.models.meal_plan import MealPlanORM
from app.models.product import ProductORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.recipe import RecipeORM
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.services.audit_service import AuditService
from app.services.catalog_import_service import CatalogImportService


def _events(db_session, *actions: str) -> list[AuditEventORM]:
    db_session.expire_all()
    statement = select(AuditEventORM).order_by(AuditEventORM.id)
    if actions:
        statement = statement.where(AuditEventORM.action.in_(actions))
    return list(db_session.scalars(statement).all())


def _serialized(event: AuditEventORM) -> str:
    return str(
        {
            "before": event.before_data,
            "after": event.after_data,
            "context": event.context_data,
        }
    )


def test_product_and_catalogue_import_audit_is_bounded_and_skips_noops(
    client,
    db_session,
):
    product_payload = {
        "name": "Рис для аудита",
        "category": "Крупы",
        "unit": "gram",
        "package_size": 900,
    }
    created = client.post("/api/v1/products", json=product_payload)
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    unchanged = client.put(f"/api/v1/products/{product_id}", json=product_payload)
    assert unchanged.status_code == 200, unchanged.text

    updated_payload = {**product_payload, "package_size": 1000}
    updated = client.put(f"/api/v1/products/{product_id}", json=updated_payload)
    assert updated.status_code == 200, updated.text

    csv_content = "\n".join(
        (
            "name,category,unit,package_size",
            "Рис для аудита,Крупы,gram,1000",
            "Гречка импорт аудит,Крупы,gram,800",
        )
    )
    imported = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "products", "content": csv_content},
    )
    assert imported.status_code == 200, imported.text
    assert imported.json()["create_count"] == 1
    assert imported.json()["skip_count"] == 1

    events = _events(
        db_session,
        "product_created",
        "product_updated",
        "catalog_import_applied",
    )
    assert [event.action for event in events] == [
        "product_created",
        "product_updated",
        "catalog_import_applied",
    ]
    assert all(event.actor_user_id == 1 for event in events)
    assert all(event.actor_display_name == "Test Administrator" for event in events)

    created_event, updated_event, import_event = events
    assert created_event.after_data["package_size"] == 900
    assert updated_event.before_data["package_size"] == 900
    assert updated_event.after_data["package_size"] == 1000
    assert import_event.after_data == {
        "kind": "products",
        "row_count": 2,
        "create_count": 1,
        "skip_count": 1,
        "component_count": 0,
        "note_count": 0,
    }
    assert csv_content not in _serialized(import_event)
    assert "Гречка импорт аудит" not in _serialized(import_event)


def test_preparation_manual_operations_and_document_generation_are_audited(
    client,
    db_session,
):
    project = ProjectORM(
        id=310,
        name="Операционный аудит",
        participants=4,
        days=1,
        status="draft",
    )
    meal_plan = MealPlanORM(
        id=str(uuid4()),
        project=project,
        name=project.name,
        participants=project.participants,
        days_count=project.days,
    )
    db_session.add_all([project, meal_plan])
    db_session.commit()

    prepared = client.post(f"/api/v1/projects/{project.id}/prepare")
    assert prepared.status_code == 200, prepared.text
    result = prepared.json()

    purchase_list_id = result["purchase_list_id"]
    checklist_id = result["purchase_checklist_id"]

    responsible_payload = {"responsible_person": "Ирина"}
    assert client.patch(
        f"/api/v1/purchase-lists/{purchase_list_id}",
        json=responsible_payload,
    ).status_code == 200
    assert client.patch(
        f"/api/v1/purchase-lists/{purchase_list_id}",
        json=responsible_payload,
    ).status_code == 200

    added = client.post(
        f"/api/v1/equipment-lists/project/{project.id}/items",
        json={"equipment_name": "Горелка", "required_quantity": 2},
    )
    assert added.status_code == 201, added.text
    equipment_item_id = added.json()["id"]
    assert client.put(
        f"/api/v1/equipment-lists/project/{project.id}/items/{equipment_item_id}",
        json={"required_quantity": 2},
    ).status_code == 200
    assert client.put(
        f"/api/v1/equipment-lists/project/{project.id}/items/{equipment_item_id}",
        json={"required_quantity": 3},
    ).status_code == 200
    assert client.delete(
        f"/api/v1/equipment-lists/project/{project.id}/items/{equipment_item_id}"
    ).status_code == 204

    product = ProductORM(
        id=str(uuid4()),
        name="Продукт чек-листа",
        category="Крупы",
        unit="gram",
    )
    checklist = db_session.get(PurchaseChecklistORM, checklist_id)
    assert checklist is not None
    checklist_item = PurchaseChecklistItemORM(
        id=str(uuid4()),
        checklist=checklist,
        product=product,
        required_quantity=Decimal("5"),
        purchased_quantity=Decimal("0"),
        unit="gram",
        is_checked=False,
    )
    db_session.add_all([product, checklist_item])
    db_session.commit()

    item_payload = {"is_checked": True, "purchased_quantity": 5}
    assert client.patch(
        f"/api/v1/purchase-checklists/items/{checklist_item.id}",
        json=item_payload,
    ).status_code == 200
    assert client.patch(
        f"/api/v1/purchase-checklists/items/{checklist_item.id}",
        json=item_payload,
    ).status_code == 200

    document = client.get(
        f"/api/v1/projects/{project.id}/documents/purchase/print"
    )
    assert document.status_code == 200, document.text

    actions = [event.action for event in _events(db_session)]
    for expected in (
        "purchase_list_generated",
        "purchase_checklist_generated",
        "equipment_list_generated",
        "project_prepared",
        "purchase_list_updated",
        "equipment_list_item_added",
        "equipment_list_item_updated",
        "equipment_list_item_deleted",
        "purchase_checklist_item_updated",
        "document_generated",
    ):
        assert expected in actions
    assert actions.count("purchase_list_updated") == 1
    assert actions.count("equipment_list_item_updated") == 1
    assert actions.count("purchase_checklist_item_updated") == 1

    document_event = _events(db_session, "document_generated")[-1]
    assert document_event.entity_type == "project_document"
    assert document_event.entity_id == str(project.id)
    assert document_event.after_data["document_kind"] == "purchase"
    assert document_event.after_data["format"] == "print"
    assert document_event.after_data["size_bytes"] > 0
    assert document.content.decode("utf-8") not in _serialized(document_event)


def test_recipe_equipment_audit_records_semantic_changes_only(client, db_session):
    recipe = RecipeORM(id=str(uuid4()), name="Рецепт с аудитом снаряжения")
    db_session.add(recipe)
    db_session.commit()

    created = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "Котел", "quantity": 2},
    )
    assert created.status_code == 201, created.text
    requirement_id = created.json()["id"]

    same_payload = {"equipment_name": "Котел", "quantity": 2}
    assert client.put(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{requirement_id}",
        json=same_payload,
    ).status_code == 200
    assert client.put(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{requirement_id}",
        json={"equipment_name": "Котел", "quantity": 3},
    ).status_code == 200
    assert client.delete(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{requirement_id}"
    ).status_code == 204

    events = _events(
        db_session,
        "recipe_equipment_created",
        "recipe_equipment_updated",
        "recipe_equipment_deleted",
    )
    assert [event.action for event in events] == [
        "recipe_equipment_created",
        "recipe_equipment_updated",
        "recipe_equipment_deleted",
    ]
    assert events[1].before_data["quantity"] == 2
    assert events[1].after_data["quantity"] == 3
    assert events[2].before_data["recipe_id"] == recipe.id


def test_catalogue_import_rolls_back_when_audit_recording_fails(
    db_session,
    monkeypatch,
):
    actor = UserORM(
        id=1,
        email="admin@test.local",
        display_name="Test Administrator",
        role="administrator",
        password_hash="not-used",
        is_active=True,
    )
    db_session.add(actor)
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    content = "\n".join(
        (
            "name,category,unit,package_size",
            "Не сохранится при ошибке аудита,Крупы,gram,500",
        )
    )
    with pytest.raises(RuntimeError, match="audit failure"):
        CatalogImportService(db_session, actor=actor).apply("products", content)

    assert db_session.scalar(
        select(ProductORM).where(
            ProductORM.name == "Не сохранится при ошибке аудита"
        )
    ) is None
    assert _events(db_session) == []
