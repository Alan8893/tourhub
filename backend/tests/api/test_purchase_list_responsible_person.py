from uuid import uuid4

from app.models.purchase_list import PurchaseListORM
from app.modules.projects.models.project import ProjectORM


def test_purchase_list_responsible_person_lifecycle(client, db_session):
    project = ProjectORM(
        id=72,
        name="Кавказ 2026",
        participants=6,
        days=4,
        status="draft",
    )
    purchase_list = PurchaseListORM(
        id=str(uuid4()),
        project_id=project.id,
        meal_plan_id=str(uuid4()),
        status="prepared",
    )
    db_session.add_all([project, purchase_list])
    db_session.commit()

    initial = client.get(f"/api/v1/purchase-lists/project/{project.id}")
    assert initial.status_code == 200
    assert initial.json()["responsible_person"] is None

    updated = client.patch(
        f"/api/v1/purchase-lists/{purchase_list.id}",
        json={"responsible_person": "  Анна Петрова  "},
    )
    assert updated.status_code == 200
    assert updated.json()["responsible_person"] == "Анна Петрова"

    persisted = client.get(f"/api/v1/purchase-lists/project/{project.id}")
    assert persisted.status_code == 200
    assert persisted.json()["responsible_person"] == "Анна Петрова"

    cleared = client.patch(
        f"/api/v1/purchase-lists/{purchase_list.id}",
        json={"responsible_person": "   "},
    )
    assert cleared.status_code == 200
    assert cleared.json()["responsible_person"] is None


def test_purchase_list_responsible_person_rejects_overlong_value(client, db_session):
    purchase_list = PurchaseListORM(
        id=str(uuid4()),
        meal_plan_id=str(uuid4()),
        status="prepared",
    )
    db_session.add(purchase_list)
    db_session.commit()

    response = client.patch(
        f"/api/v1/purchase-lists/{purchase_list.id}",
        json={"responsible_person": "А" * 256},
    )

    assert response.status_code == 422
