from uuid import uuid4

from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.modules.projects.models.project import ProjectORM


def test_project_purchase_list_exposes_package_quantity_and_surplus(client, db_session):
    project = ProjectORM(
        id=1,
        name="Алтай 2026",
        participants=8,
        days=5,
        status="draft",
    )
    product = ProductORM(
        id=str(uuid4()),
        name="Рис",
        category="cereal",
        unit="gram",
        package_size=400,
    )
    purchase_list = PurchaseListORM(
        id=str(uuid4()),
        project_id=project.id,
        meal_plan_id=str(uuid4()),
        status="prepared",
    )
    item = PurchaseListItemORM(
        id=str(uuid4()),
        purchase_list=purchase_list,
        product=product,
        required_quantity=1000,
        required_unit="gram",
        package_size=400,
        package_unit="gram",
        packages_count=3,
    )

    db_session.add_all([project, product, purchase_list, item])
    db_session.commit()

    response = client.get("/api/v1/purchase-lists/project/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"] == [
        {
            "id": item.id,
            "product_id": product.id,
            "product_name": "Рис",
            "required_quantity": 1000.0,
            "required_unit": "gram",
            "package_size": 400.0,
            "package_unit": "gram",
            "packages_count": 3,
            "purchase_quantity": 1200.0,
            "surplus_quantity": 200.0,
        }
    ]
