from io import BytesIO
from datetime import datetime, timezone

from reportlab.pdfgen import canvas

from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class PDFDocumentGenerator:
    """Generate PDF purchase documents."""

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        pdf.drawString(50, 800, document.title)

        y_position = 770

        for item in document.items:
            pdf.drawString(
                50,
                y_position,
                f"{item.product_name}: {item.quantity} {item.unit}",
            )
            y_position -= 20

        pdf.save()

        return GeneratedDocument(
            filename="purchase_list.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(timezone.utc),
            content=buffer.getvalue(),
        )
