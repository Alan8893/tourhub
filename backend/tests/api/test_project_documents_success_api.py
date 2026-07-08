from app.main import app
from app.core.database import get_db
from app.modules.projects.models.project import ProjectORM
from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM



def override_test_db(db_session):
    def _override():
        yield db_session

    return _override



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

    db_session.add(project)
    db_session.flush()

    purchase_list = PurchaseListORM(
        id="purchase-doc-test",
        project_id=project.id,
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

    db_session.add_all([product, purchase_list, item])
    db_session.commit()

    return project.id



def test_project_purchase_pdf_document(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/pdf"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    app.dependency_overrides.clear()



def test_project_purchase_print_document(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/print"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    app.dependency_overrides.clear()



def test_project_purchase_excel_document(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/excel"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    app.dependency_overrides.clear()
