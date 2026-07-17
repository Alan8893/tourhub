from dataclasses import dataclass, field


@dataclass(frozen=True)
class DocumentPaletteDTO:
    primary_color: str = "#1B5E20"
    accent_color: str = "#F9A825"
    heading_color: str = "#1B5E20"
    table_header_background: str = "#E8F2E8"
    table_header_text: str = "#162018"
    table_border_color: str = "#405047"
    title_background_color: str = "#F4F7F4"


@dataclass(frozen=True)
class ClubBrandingDTO:
    """Immutable club and document appearance snapshot for one generation request."""

    club_name: str
    logo_bytes: bytes | None = None
    logo_mime_type: str | None = None
    contact_lines: tuple[str, ...] = ()
    footer_text: str | None = None
    palette: DocumentPaletteDTO = field(default_factory=DocumentPaletteDTO)
    table_density: str = "comfortable"
    title_background_bytes: bytes | None = None
    title_background_mime_type: str | None = None
