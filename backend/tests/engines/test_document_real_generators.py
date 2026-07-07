from zipfile import ZipFile
from io import BytesIO

from app.engines.documents.dto import (
    DocumentItemDTO,
    PurchaseDocumentDTO,
)
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator


def create_document():
    return PurchaseDocumentDTO(
        purchase_list_id="purchase-1",
        title="Purchase List",
        items=[
            DocumentItemDTO(
                product_name="Rice",
                quantity=2000,
                unit="gram",
                packages_count=2,
            )
        ],
    )


def test_pdf_generator_creates_file():
    result = PDFDocumentGenerator().generate(
        create_document()
    )

    assert result.content
    assert result.content.startswith(b"%PDF")


def test_excel_generator_creates_file():
    result = ExcelDocumentGenerator().generate(
        create_document()
    )

    assert result.content

    with ZipFile(BytesIO(result.content)) as archive:
        assert "xl/workbook.xml" in archive.namelist()
