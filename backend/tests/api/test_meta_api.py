from app.domain.workflows.purchase_checklist import PurchaseChecklistStatus
from app.domain.workflows.purchase_list import PurchaseListStatus


def test_meta_endpoint_returns_api_information(client):
    response = client.get("/api/v1/meta")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "TourHub"
    assert data["api_version"] == "v1"


def test_meta_endpoint_returns_workflow_statuses(client):
    response = client.get("/api/v1/meta")

    data = response.json()

    assert data["statuses"]["purchase_list"] == [
        status.value for status in PurchaseListStatus
    ]

    assert data["statuses"]["purchase_checklist"] == [
        status.value for status in PurchaseChecklistStatus
    ]


def test_openapi_contains_meta_endpoint(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "/api/v1/meta" in schema["paths"]
