from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class PrintDocumentGenerator:
    """Generate printable text representation."""

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        lines = [document.title, ""]

        for item in document.items:
            lines.append(
                f"{item.product_name}: {item.quantity} {item.unit}"
            )

        return GeneratedDocument(
            filename="purchase_list.txt",
            content_type="text/plain",
            generated_at=__import__("datetime").datetime.utcnow(),
            content="\n".join(lines),
        )
