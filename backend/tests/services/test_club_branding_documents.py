from datetime import UTC, datetime
from io import BytesIO
from types import SimpleNamespace

from openpyxl import load_workbook
from PIL import Image

from app.engines.documents.branding import ClubBrandingDTO, DocumentPaletteDTO
from app.engines.documents.dto import (
    DocumentItemDTO,
    GeneratedDocument,
    PurchaseDocumentDTO,
)
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator
from app.engines.documents.printer import PrintDocumentGenerator
from app.services.project_document_service import ProjectDocumentService


def _logo_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (16, 8), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def _purchase_dto() -> PurchaseDocumentDTO:
    return PurchaseDocumentDTO(
        purchase_list_id="purchase-1",
        title="Закупочный лист",
        items=[DocumentItemDTO(product_name="Крупа", quantity=2, unit="кг")],
    )


def test_pdf_excel_and_print_accept_configured_document_branding() -> None:
    branding = ClubBrandingDTO(
        club_name="Турклуб Север",
        logo_bytes=_logo_bytes(),
        logo_mime_type="image/png",
        contact_lines=("Москва", "Тел.: +7 900 000-00-00"),
        footer_text="Внутренний документ клуба",
        palette=DocumentPaletteDTO(
            primary_color="#075985",
            accent_color="#0F766E",
            heading_color="#075985",
            table_header_background="#075985",
            table_header_text="#FFFFFF",
            table_border_color="#0F172A",
            title_background_color="#E0F2FE",
        ),
        table_density="compact",
        title_background_bytes=_logo_bytes(),
        title_background_mime_type="image/png",
    )

    pdf = PDFDocumentGenerator().generate(_purchase_dto(), branding)
    assert bytes(pdf.content).startswith(b"%PDF")

    excel = ExcelDocumentGenerator().generate(_purchase_dto(), branding)
    workbook = load_workbook(BytesIO(bytes(excel.content)))
    sheet = workbook["Закупка"]
    assert workbook.properties.creator == "Турклуб Север"
    assert sheet.oddHeader.center.text == "Турклуб Север"
    assert sheet.oddFooter.left.text == "Внутренний документ клуба"
    assert len(sheet._images) == 2
    assert sheet["F4"].value == "Москва"
    assert sheet["F5"].value == "Тел.: +7 900 000-00-00"
    assert sheet["A1"].fill.fgColor.rgb.endswith("E0F2FE")
    assert sheet["A4"].fill.fgColor.rgb.endswith("075985")
    assert sheet.row_dimensions[4].height == 18

    printable = PrintDocumentGenerator().generate(_purchase_dto(), branding)
    text = str(printable.content)
    assert "Турклуб Север" in text
    assert "Тел.: +7 900 000-00-00" in text
    assert "Внутренний документ клуба" in text


class FakeSettingsService:
    def __init__(self, branding: ClubBrandingDTO) -> None:
        self.branding = branding
        self.calls = 0

    def to_branding(self) -> ClubBrandingDTO:
        self.calls += 1
        return self.branding


class FakeClubSettingsService:
    def __init__(self) -> None:
        self.club = SimpleNamespace(club_name="Турклуб Север")
        self.get_calls = 0

    def get(self):
        self.get_calls += 1
        return self.club


class FakeDocumentAppearanceService:
    def __init__(self, branding: ClubBrandingDTO) -> None:
        self.branding = branding
        self.calls = 0
        self.clubs = []

    def to_branding(self, club) -> ClubBrandingDTO:
        self.calls += 1
        self.clubs.append(club)
        return self.branding


class FakeMapper:
    def to_dto(self, purchase_list) -> PurchaseDocumentDTO:
        del purchase_list
        return _purchase_dto()


class CapturingGenerator:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.brandings: list[ClubBrandingDTO | None] = []

    def generate(self, document, branding=None) -> GeneratedDocument:
        del document
        self.brandings.append(branding)
        return GeneratedDocument(
            filename=self.filename,
            content_type="application/octet-stream",
            generated_at=datetime.now(UTC),
            content=b"document",
        )


def test_project_document_service_reuses_legacy_brand_snapshot() -> None:
    branding = ClubBrandingDTO(club_name="Турклуб Север")
    settings_service = FakeSettingsService(branding)
    pdf_generator = CapturingGenerator("purchase.pdf")
    excel_generator = CapturingGenerator("purchase.xlsx")
    service = ProjectDocumentService(
        document_mapper=FakeMapper(),
        pdf_generator=pdf_generator,
        excel_generator=excel_generator,
        club_settings_service=settings_service,
    )
    project = SimpleNamespace(purchase_lists=[SimpleNamespace()], meal_plans=[])

    service.generate_purchase_pdf(project)
    service.generate_purchase_excel(project)

    assert settings_service.calls == 1
    assert pdf_generator.brandings == [branding]
    assert excel_generator.brandings == [branding]


def test_project_document_service_reuses_one_combined_snapshot() -> None:
    branding = ClubBrandingDTO(
        club_name="Турклуб Север",
        footer_text="Один snapshot",
    )
    club_service = FakeClubSettingsService()
    appearance_service = FakeDocumentAppearanceService(branding)
    pdf_generator = CapturingGenerator("purchase.pdf")
    excel_generator = CapturingGenerator("purchase.xlsx")
    print_generator = CapturingGenerator("purchase.txt")
    service = ProjectDocumentService(
        document_mapper=FakeMapper(),
        pdf_generator=pdf_generator,
        excel_generator=excel_generator,
        print_generator=print_generator,
        club_settings_service=club_service,
        document_appearance_service=appearance_service,
    )
    project = SimpleNamespace(purchase_lists=[SimpleNamespace()], meal_plans=[])

    service.generate_purchase_pdf(project)
    service.generate_purchase_excel(project)
    service.generate_purchase_print(project)

    assert club_service.get_calls == 1
    assert appearance_service.calls == 1
    assert appearance_service.clubs == [club_service.club]
    captured = [
        pdf_generator.brandings[0],
        excel_generator.brandings[0],
        print_generator.brandings[0],
    ]
    assert all(item is branding for item in captured)
