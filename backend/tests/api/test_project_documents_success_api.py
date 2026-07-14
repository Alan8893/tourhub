from app.core.database import get_db
from app.main import app
from app.models.meal_plan import MealPlanORM
from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.modules.projects.models.project import ProjectORM


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


def create_legacy_project_with_purchase_list(db_session):
    product = ProductORM(
        id="product-doc-legacy",
        name="Rice Legacy Document Test",
        category="food",
        unit="gram",
    )
    project = ProjectORM(
        name="Legacy Document Test Project",
        participants=4,
        days=3,
        status="prepared",
    )
    db_session.add(project)
    db_session.flush()

    meal_plan = MealPlanORM(
        id="meal-plan-doc-legacy",
        project_id=project.id,
        name="Legacy meal plan",
        participants=4,
        days_count=3,
    )
    purchase_list = PurchaseListORM(
        id="purchase-doc-legacy",
        project_id=None,
        meal_plan_id=meal_plan.id,
        status="ready",
    )
    item = PurchaseListItemORM(
        id="purchase-item-doc-legacy",
        purchase_list=purchase_list,
        product=product,
        required_quantity=1000,
        required_unit="gram",
        package_size=1000,
        package_unit="gram",
        packages_count=1,
    )

    db_session.add_all([product, meal_plan, purchase_list, item])
    db_session.commit()

    return project.id


def create_project_without_purchase_list(db_session):
    project = ProjectORM(
        name="Unprepared Document Project",
        participants=4,
        days=3,
        status="draft",
    )
    db_session.add(project)
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


def test_project_purchase_pdf_document_for_legacy_link(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_legacy_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/pdf"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    app.dependency_overrides.clear()


def test_project_purchase_document_requires_preparation(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_project_without_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/purchase/pdf"
    )

    assert response.status_code == 409
    assert response.json()["error"] == "Project purchasing is not prepared"

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
