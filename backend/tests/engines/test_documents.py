from app.engines.documents.dto import (
    DocumentItemDTO,
    PurchaseDocumentDTO,
)
from app.engines.documents.printer import PrintDocumentGenerator


def test_print_document_generator():
    document = PurchaseDocumentDTO(
        purchase_list_id="purchase-1",
        title="Purchase List",
        items=[
            DocumentItemDTO(
                product_name="Rice",
                quantity=1000,
                unit="gram",
            )
        ],
    )

    result = PrintDocumentGenerator().generate(document)

    assert result.filename == "purchase_list.txt"
    assert result.content_type == "text/plain"
    assert "Rice" in result.content
