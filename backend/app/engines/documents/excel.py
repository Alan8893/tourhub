from io import BytesIO
from datetime import datetime, timezone

from openpyxl import Workbook

from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class ExcelDocumentGenerator:
    """Generate XLSX purchase documents."""

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Purchase List"

        sheet.append([
            "Product",
            "Quantity",
            "Unit",
            "Packages",
        ])

        for item in document.items:
            sheet.append([
                item.product_name,
                item.quantity,
                item.unit,
                item.packages_count,
            ])

        buffer = BytesIO()
        workbook.save(buffer)

        return GeneratedDocument(
            filename="purchase_list.xlsx",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            generated_at=datetime.now(timezone.utc),
            content=buffer.getvalue(),
        )
