from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)
from datetime import datetime, timezone

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
            generated_at=datetime.now(timezone.utc),
            content="\n".join(lines),
        )
