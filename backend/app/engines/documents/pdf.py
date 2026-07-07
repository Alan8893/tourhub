from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class PDFDocumentGenerator:
    """PDF document generator contract.

    Real PDF rendering will be implemented after
    selecting the PDF infrastructure library.
    """

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        return GeneratedDocument(
            filename="purchase_list.pdf",
            content_type="application/pdf",
            generated_at=__import__("datetime").datetime.utcnow(),
            content=b"",
        )
