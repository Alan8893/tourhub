from datetime import datetime, timezone
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font

from app.engines.documents.dto import GeneratedDocument, PurchaseDocumentDTO


class ExcelDocumentGenerator:
    """Generate Russian XLSX purchase documents."""

    def generate(self, document: PurchaseDocumentDTO) -> GeneratedDocument:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Закупка"
        sheet.append([document.title])
        sheet.append(["Идентификатор списка", document.purchase_list_id])
        sheet.append([])
        sheet.append(["Продукт", "Количество", "Единица", "Упаковок"])
        for cell in sheet[4]:
            cell.font = Font(bold=True)

        for item in document.items:
            sheet.append(
                [
                    item.product_name,
                    item.quantity,
                    item.unit,
                    item.packages_count,
                ]
            )

        sheet.freeze_panes = "A5"
        sheet.column_dimensions["A"].width = 34
        sheet.column_dimensions["B"].width = 14
        sheet.column_dimensions["C"].width = 16
        sheet.column_dimensions["D"].width = 14
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
