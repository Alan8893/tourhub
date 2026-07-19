from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from textwrap import wrap
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.engines.documents.branding import ClubBrandingDTO
from app.engines.documents.branding_render import (
    apply_pdf_heading_styles,
    pdf_branding_flowables,
    pdf_table_style_commands,
)
from app.engines.documents.consolidated_dto import ConsolidatedProjectDocumentDTO
from app.engines.documents.dto import GeneratedDocument

_GENERATION_MODE_LABELS = {
    "club_only": "Только клубные рецепты",
    "club_and_personal": "Клубные и личные рецепты",
    "personal_preferred": "Личные рецепты в приоритете",
}
_STATUS_LABELS = {
    "draft": "Черновик",
    "prepared": "Подготовлен",
    "ready": "Готов",
}


class ConsolidatedPDFDocumentGenerator:
    """Generate the complete Russian Project PDF defined by PRODUCT_SPEC."""

    @staticmethod
    def _register_font() -> str:
        font_name = "TourHubUnicode"
        try:
            pdfmetrics.getFont(font_name)
            return font_name
        except KeyError:
            pass

        candidates = [
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        for path in candidates:
            if path.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(path)))
                return font_name
        raise RuntimeError(
            "Unicode PDF font not found. Install a font with Cyrillic support."
        )

    @staticmethod
    def _footer(
        branding: ClubBrandingDTO | None,
    ) -> Callable[[Any, Any], None]:
        def draw_footer(canvas: Any, document: Any) -> None:
            del document
            canvas.saveState()
            canvas.setFont("TourHubUnicode", 8)
            if branding is not None:
                canvas.setFillColor(colors.HexColor(branding.palette.primary_color))
            label = (
                branding.footer_text
                if branding is not None and branding.footer_text
                else (
                    f"Сформировано для {branding.club_name} в TourHub"
                    if branding is not None
                    else "Сформировано в TourHub"
                )
            )
            for index, line in enumerate(reversed(wrap(label, width=115)[:2])):
                canvas.drawString(12 * mm, (7 + index * 3) * mm, line)
            canvas.drawRightString(
                285 * mm,
                9 * mm,
                f"Страница {canvas.getPageNumber()}",
            )
            canvas.restoreState()

        return draw_footer

    @staticmethod
    def _cell(value: object, style: Any) -> Paragraph:
        text = "—" if value is None or value == "" else str(value)
        return Paragraph(escape(text), style)

    def _table(
        self,
        *,
        headers: Sequence[str],
        rows: Sequence[Sequence[object]],
        styles: Any,
        branding: ClubBrandingDTO | None,
        font_name: str,
        column_widths: Sequence[float] | None = None,
    ) -> Table:
        body_style = styles["BodyText"].clone("TourHubTableBody")
        body_style.fontName = font_name
        body_style.fontSize = 8
        body_style.leading = 10

        data: list[list[Paragraph]] = [
            [self._cell(header, body_style) for header in headers]
        ]
        source_rows = rows or [["Нет данных", *("" for _ in headers[1:])]]
        data.extend(
            [self._cell(value, body_style) for value in row]
            for row in source_rows
        )
        table = Table(
            data,
            colWidths=list(column_widths) if column_widths is not None else None,
            repeatRows=1,
            hAlign="LEFT",
        )
        commands = pdf_table_style_commands(branding, font_name=font_name)
        commands.append(("LEFTPADDING", (0, 0), (-1, -1), 4))
        commands.append(("RIGHTPADDING", (0, 0), (-1, -1), 4))
        table.setStyle(TableStyle(commands))
        return table

    def generate(
        self,
        document: ConsolidatedProjectDocumentDTO,
        branding: ClubBrandingDTO | None = None,
    ) -> GeneratedDocument:
        buffer = BytesIO()
        font_name = self._register_font()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=12 * mm,
            leftMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=16 * mm,
            title=f"Документы похода — {document.summary.project_name}",
        )
        styles = getSampleStyleSheet()
        for style in styles.byName.values():
            style.fontName = font_name
        apply_pdf_heading_styles(styles, branding)

        summary_rows = [
            ["Название", document.summary.project_name],
            ["Участников", document.summary.participants],
            ["Дней", document.summary.days],
            ["Дата начала", document.summary.start_date or "Не указана"],
            ["Первый приём пищи", document.summary.first_meal or "Не указан"],
            ["Последний приём пищи", document.summary.last_meal or "Не указан"],
            [
                "Режим рецептов",
                _GENERATION_MODE_LABELS.get(
                    document.summary.recipe_generation_mode,
                    document.summary.recipe_generation_mode,
                ),
            ],
            [
                "Статус",
                _STATUS_LABELS.get(document.summary.status, document.summary.status),
            ],
        ]

        content: list[Any] = [
            *pdf_branding_flowables(styles, branding),
            Paragraph("Документы похода", styles["Title"]),
            Paragraph(document.summary.project_name, styles["Heading2"]),
            Spacer(1, 5 * mm),
            Paragraph("Параметры похода", styles["Heading1"]),
            self._table(
                headers=["Параметр", "Значение"],
                rows=summary_rows,
                styles=styles,
                branding=branding,
                font_name=font_name,
                column_widths=[55 * mm, 190 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Меню по дням", styles["Heading1"]),
            self._table(
                headers=[
                    "День",
                    "Приём пищи",
                    "Блюдо",
                    "Рецепт",
                    "Источник",
                ],
                rows=[
                    [
                        row.day_number,
                        row.meal_name,
                        row.dish_name,
                        row.recipe_name,
                        "Вручную" if row.is_manually_edited else "Автоматически",
                    ]
                    for row in document.menu_rows
                ],
                styles=styles,
                branding=branding,
                font_name=font_name,
                column_widths=[15 * mm, 35 * mm, 70 * mm, 80 * mm, 35 * mm],
            ),
            PageBreak(),
            Paragraph("Раскладка", styles["Heading1"]),
            self._table(
                headers=["Продукт", "Категория", "Количество", "Единица"],
                rows=[
                    [
                        row.product_name,
                        row.category,
                        row.required_quantity,
                        row.required_unit,
                    ]
                    for row in document.loadout_rows
                ],
                styles=styles,
                branding=branding,
                font_name=font_name,
                column_widths=[95 * mm, 55 * mm, 40 * mm, 40 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Закупка", styles["Heading1"]),
            self._table(
                headers=[
                    "Продукт",
                    "Нужно",
                    "Упаковка",
                    "Упаковок",
                    "Купить",
                    "Остаток",
                    "Куплено",
                    "Статус / комментарий",
                ],
                rows=[
                    [
                        row.product_name,
                        f"{row.required_quantity:g} {row.required_unit}",
                        f"{row.package_size:g} {row.package_unit}",
                        row.packages_count,
                        f"{row.purchase_quantity:g} {row.package_unit}",
                        f"{row.surplus_quantity:g} {row.package_unit}",
                        f"{row.purchased_quantity:g} {row.required_unit}",
                        (
                            ("Куплено" if row.is_checked else "Не куплено")
                            + (f": {row.comment}" if row.comment else "")
                        ),
                    ]
                    for row in document.purchase_rows
                ],
                styles=styles,
                branding=branding,
                font_name=font_name,
                column_widths=[
                    52 * mm,
                    30 * mm,
                    30 * mm,
                    20 * mm,
                    30 * mm,
                    30 * mm,
                    30 * mm,
                    55 * mm,
                ],
            ),
            PageBreak(),
            Paragraph("Оборудование", styles["Heading1"]),
            self._table(
                headers=[
                    "Оборудование",
                    "Требуется",
                    "Расчёт",
                    "Источник",
                ],
                rows=[
                    [
                        row.equipment_name,
                        row.required_quantity,
                        row.calculated_quantity,
                        row.source,
                    ]
                    for row in document.equipment_rows
                ],
                styles=styles,
                branding=branding,
                font_name=font_name,
                column_widths=[115 * mm, 35 * mm, 35 * mm, 70 * mm],
            ),
            Spacer(1, 6 * mm),
            Paragraph("Предупреждения и комментарии", styles["Heading1"]),
        ]

        if document.responsible_person:
            content.append(
                Paragraph(
                    f"Ответственный за закупку: {escape(document.responsible_person)}",
                    styles["Normal"],
                )
            )
            content.append(Spacer(1, 2 * mm))

        notes = [
            *(f"Предупреждение: {warning}" for warning in document.warnings),
            *(f"Комментарий: {comment}" for comment in document.comments),
        ]
        if not notes:
            content.append(Paragraph("Предупреждений и комментариев нет.", styles["Normal"]))
        else:
            for note in notes:
                content.append(Paragraph(f"• {escape(note)}", styles["Normal"]))
                content.append(Spacer(1, 1.5 * mm))

        footer = self._footer(branding)
        pdf.build(content, onFirstPage=footer, onLaterPages=footer)
        return GeneratedDocument(
            filename=f"tourhub_project_{document.summary.project_id}_complete.pdf",
            content_type="application/pdf",
            generated_at=datetime.now(UTC),
            content=buffer.getvalue(),
        )
