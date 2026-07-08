def test_project_document_not_found(client):
    response = client.get(
        "/api/v1/projects/999999/documents/purchase/pdf"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_project_document_unsupported_format(client):
    response = client.get(
        "/api/v1/projects/999999/documents/purchase/unknown"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"
