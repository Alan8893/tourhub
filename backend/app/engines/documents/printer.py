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
            package_text = ""
            if item.packages_count:
                package_text = f" (packages: {item.packages_count}"
                if item.package_size:
                    package_text += f" x {item.package_size}"
                package_text += ")"

            lines.append(
                f"{item.product_name}: {item.quantity} {item.unit}{package_text}"
            )

        return GeneratedDocument(
            filename="purchase_list.txt",
            content_type="text/plain",
            generated_at=datetime.now(timezone.utc),
            content="\n".join(lines),
        )
