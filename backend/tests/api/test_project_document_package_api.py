from io import BytesIO
from zipfile import ZipFile

from app.core.database import get_db
from app.main import app

from tests.api.test_project_documents_success_api import (
    create_project_with_purchase_list,
    override_test_db,
)



def test_project_document_package(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    project_id = create_project_with_purchase_list(db_session)

    response = client.get(
        f"/api/v1/projects/{project_id}/documents/package"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    archive = ZipFile(BytesIO(response.content))
    filenames = archive.namelist()

    assert "purchase_list.pdf" in filenames
    assert "purchase_list.xlsx" in filenames
    assert "purchase_list.txt" in filenames

    app.dependency_overrides.clear()



def test_project_document_package_not_found(client, db_session):
    app.dependency_overrides[get_db] = override_test_db(db_session)

    response = client.get(
        "/api/v1/projects/999999/documents/package"
    )

    assert response.status_code == 404
    assert response.json()["error"] == "Project not found"

    app.dependency_overrides.clear()
