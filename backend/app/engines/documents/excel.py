from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class ExcelDocumentGenerator:
    """Excel document generator contract.

    Real XLSX generation will be implemented after
    selecting the spreadsheet infrastructure library.
    """

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        return GeneratedDocument(
            filename="purchase_list.xlsx",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            generated_at=__import__("datetime").datetime.utcnow(),
            content=b"",
        )
