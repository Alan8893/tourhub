from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.engines.documents.dto import GeneratedDocument, PurchaseDocumentDTO


class PDFDocumentGenerator:
    """Generate Russian PDF purchase documents."""

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
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]

        for font_path in font_candidates:
            if font_path.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                return font_name

        raise RuntimeError(
            "Unicode PDF font not found. Install a font with Cyrillic support."
        )

    def _footer(self, canvas, document):
        canvas.saveState()
        canvas.setFont("TourHubUnicode", 8)
        canvas.drawString(20 * mm, 10 * mm, "Сформировано в TourHub")
        canvas.drawRightString(
            190 * mm,
            10 * mm,
            f"Страница {canvas.getPageNumber()}",
        )
        canvas.restoreState()

    def generate(self, document: PurchaseDocumentDTO) -> GeneratedDocument:
        buffer = BytesIO()
        font_name = self._register_font()

        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        for style in styles.byName.values():
            style.fontName = font_name

        content = [
            Paragraph(document.title, styles["Title"]),
            Spacer(1, 10 * mm),
            Paragraph(
                f"Идентификатор списка: {document.purchase_list_id}",
                styles["Normal"],
            ),
            Spacer(1, 5 * mm),
        ]

        table_data = [
            [
                "Продукт",
                "Количество",
                "Единица",
                "Размер упаковки",
                "Упаковок",
            ]
        ]

        for item in document.items:
            table_data.append(
                [
                    item.product_name,
                    str(item.quantity),
                    item.unit,
                    str(item.package_size) if item.package_size is not None else "—",
                    str(item.packages_count) if item.packages_count is not None else "—",
                ]
            )

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), font_name, 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )

        content.append(table)

        pdf.build(
            content,
            onFirstPage=self._footer,
            onLaterPages=self._footer,
        )

        return GeneratedDocument(
            filename="purchase_list.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(timezone.utc),
            content=buffer.getvalue(),
        )
