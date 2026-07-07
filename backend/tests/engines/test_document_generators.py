from app.engines.documents.dto import PurchaseDocumentDTO
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator


def test_pdf_generator_contract():
    result = PDFDocumentGenerator().generate(
        PurchaseDocumentDTO(
            purchase_list_id="purchase-1",
            title="Purchase List",
            items=[],
        )
    )

    assert result.filename == "purchase_list.pdf"
    assert result.content_type == "application/pdf"


def test_excel_generator_contract():
    result = ExcelDocumentGenerator().generate(
        PurchaseDocumentDTO(
            purchase_list_id="purchase-1",
            title="Purchase List",
            items=[],
        )
    )

    assert result.filename == "purchase_list.xlsx"
    assert "spreadsheetml" in result.content_type
