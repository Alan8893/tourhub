from io import BytesIO
from typing import Any

from openpyxl.drawing.image import Image as ExcelImage
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image as PDFImage
from reportlab.platypus import Paragraph, Spacer

from app.engines.documents.branding import ClubBrandingDTO


def pdf_branding_flowables(
    styles: Any,
    branding: ClubBrandingDTO | None,
) -> list[Any]:
    if branding is None:
        return []

    flowables: list[Any] = []
    if branding.logo_bytes is not None:
        image_data = BytesIO(branding.logo_bytes)
        width, height = ImageReader(image_data).getSize()
        scale = min((28 * mm) / width, (18 * mm) / height)
        image_data.seek(0)
        flowables.append(
            PDFImage(
                image_data,
                width=width * scale,
                height=height * scale,
            )
        )
        flowables.append(Spacer(1, 2 * mm))

    flowables.append(Paragraph(branding.club_name, styles["Heading2"]))
    flowables.append(Spacer(1, 3 * mm))
    return flowables


def apply_excel_branding(
    workbook: Any,
    sheet: Any,
    branding: ClubBrandingDTO | None,
) -> None:
    if branding is None:
        return

    workbook.properties.creator = branding.club_name
    sheet.oddHeader.center.text = branding.club_name
    if branding.logo_bytes is None:
        return

    logo = ExcelImage(BytesIO(branding.logo_bytes))
    max_width = 120
    max_height = 60
    scale = min(max_width / logo.width, max_height / logo.height, 1)
    logo.width *= scale
    logo.height *= scale
    sheet.add_image(logo, "F1")
