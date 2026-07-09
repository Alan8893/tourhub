from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path

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
        font_name = "TourHubUnicode"

        try:
            pdfmetrics.getFont(font_name)
            return font_name
        except KeyError:
            pass

        font_candidates = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
        ]

        for font_path in font_candidates:
            if font_path.exists():
                pdfmetrics.registerFont(
                    TTFont(font_name, str(font_path))
                )
                return font_name

        raise RuntimeError(
            "Unicode PDF font not found. Install a font with Cyrillic support."
        )

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
