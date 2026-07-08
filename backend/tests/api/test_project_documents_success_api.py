from app.modules.projects.models.project import ProjectORM
from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM


def create_project_with_purchase_list(db_session):
    product = ProductORM(
        id="product-doc-test",
        name="Rice Document Test",
        category="food",
        unit="gram",
    )

    project = ProjectORM(
        name="Document Test Project",
        participants=4,
        days=3,
        status="prepared",
    )

    purchase_list = PurchaseListORM(
        id="purchase-doc-test",
        project=project,
        meal_plan_id="meal-plan-doc-test",
        status="ready",
    )

    item = PurchaseListItemORM(
        id="purchase-item-doc-test",
        purchase_list=purchase_list,
        product=product,
        required_quantity=1000,
        required_unit="gram",
        package_size=1000,
        package_unit="gram",
        packages_count=1,
    )

    db_session.add_all([product, project, purchase_list, item])
    db_session.commit()

    return project.id


def test_project_purchase_pdf_document(client, db_session):
    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/pdf"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_project_purchase_print_document(client, db_session):
    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/print"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
