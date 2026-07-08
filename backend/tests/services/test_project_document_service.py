from types import SimpleNamespace

import pytest

from app.services.project_document_service import ProjectDocumentService


class FakePurchaseList:
    id = "purchase-1"
    items = []


class FakeProject:
    purchase_lists = [FakePurchaseList()]


def test_project_document_service_missing_purchase_list():
    project = SimpleNamespace(purchase_lists=[])

    with pytest.raises(ValueError, match="Purchase list not found"):
        ProjectDocumentService().generate_purchase_pdf(project)


def test_project_document_service_generators_are_configured():
    service = ProjectDocumentService()

    assert service.pdf_generator is not None
    assert service.excel_generator is not None
    assert service.print_generator is not None
