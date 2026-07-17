from datetime import UTC, datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.engines.documents.branding import ClubBrandingDTO
from app.engines.documents.branding_render import pdf_branding_flowables
from app.engines.documents.dto import GeneratedDocument
from app.engines.documents.equipment_dto import EquipmentDocumentDTO
from app.engines.documents.pdf import PDFDocumentGenerator


class EquipmentPDFDocumentGenerator(PDFDocumentGenerator):
    """Generate a Russian PDF with final and calculated equipment quantities."""

    def generate(
        self,
        document: EquipmentDocumentDTO,
        branding: ClubBrandingDTO | None = None,
    ) -> GeneratedDocument:
        buffer = BytesIO()
        font_name = self._register_font()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=18 * mm,
            bottomMargin=20 * mm,
        )
        styles = getSampleStyleSheet()
        for style in styles.byName.values():
            style.fontName = font_name

        content = [
            *pdf_branding_flowables(styles, branding),
            Paragraph(document.title, styles["Title"]),
            Spacer(1, 5 * mm),
            Paragraph(f"Проект: {document.project_name}", styles["Normal"]),
            Paragraph(
                f"Идентификатор списка: {document.equipment_list_id}",
                styles["Normal"],
            ),
            Spacer(1, 5 * mm),
        ]
        table_data = [["Оборудование", "Итого, шт.", "Расчёт, шт.", "Источник"]]
        for item in document.items:
            table_data.append(
                [
                    item.equipment_name,
                    str(item.required_quantity),
                    str(item.calculated_quantity) if item.calculated_quantity is not None else "—",
                    item.source,
                ]
            )

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[75 * mm, 25 * mm, 27 * mm, 43 * mm],
        )
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), font_name, 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (1, 1), (2, -1), "CENTER"),
                ]
            )
        )
        content.append(table)
        footer = self._footer(branding)
        pdf.build(content, onFirstPage=footer, onLaterPages=footer)
        return GeneratedDocument(
            filename="equipment_list.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(UTC),
            content=buffer.getvalue(),
        )
