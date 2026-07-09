from io import BytesIO
from datetime import datetime, timezone

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from app.engines.documents.dto import (
    GeneratedDocument,
    PurchaseDocumentDTO,
)


class PDFDocumentGenerator:
    """Generate PDF purchase documents."""

    def _register_font(self) -> str:
        font_name = "DejaVuSans"
        try:
            pdfmetrics.getFont(font_name)
        except KeyError:
            pdfmetrics.registerFont(
                TTFont(font_name, "DejaVuSans.ttf")
            )
        return font_name

    def generate(
        self,
        document: PurchaseDocumentDTO,
    ) -> GeneratedDocument:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)

        font_name = self._register_font()
        pdf.setFont(font_name, 14)
        pdf.drawString(50, 800, document.title)

        pdf.setFont(font_name, 10)
        y_position = 770

        for item in document.items:
            package_text = ""
            if item.packages_count:
                package_text = f" | Packages: {item.packages_count}"
                if item.package_size:
                    package_text += f" x {item.package_size}"

            pdf.drawString(
                50,
                y_position,
                f"{item.product_name}: {item.quantity} {item.unit}{package_text}",
            )
            y_position -= 20

        pdf.save()

        return GeneratedDocument(
            filename="purchase_list.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(timezone.utc),
            content=buffer.getvalue(),
        )
