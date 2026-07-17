from collections.abc import Callable
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.engines.documents.branding import ClubBrandingDTO
from app.engines.documents.branding_render import pdf_branding_flowables
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

    def _footer(
        self,
        branding: ClubBrandingDTO | None,
    ) -> Callable[[Any, Any], None]:
        def draw_footer(canvas: Any, document: Any) -> None:
            del document
            canvas.saveState()
            canvas.setFont("TourHubUnicode", 8)
            label = (
                f"Сформировано для {branding.club_name} в TourHub"
                if branding is not None
                else "Сформировано в TourHub"
            )
            canvas.drawString(20 * mm, 10 * mm, label)
            canvas.drawRightString(
                190 * mm,
                10 * mm,
                f"Страница {canvas.getPageNumber()}",
            )
            canvas.restoreState()

        return draw_footer

    def generate(
        self,
        document: PurchaseDocumentDTO,
        branding: ClubBrandingDTO | None = None,
    ) -> GeneratedDocument:
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
            *pdf_branding_flowables(styles, branding),
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
        footer = self._footer(branding)
        pdf.build(content, onFirstPage=footer, onLaterPages=footer)

        return GeneratedDocument(
            filename="purchase_list.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(UTC),
            content=buffer.getvalue(),
        )
