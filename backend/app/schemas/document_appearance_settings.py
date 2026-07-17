from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentLogoSource(StrEnum):
    MAIN_LOGO = "main_logo"
    DOCUMENT_IMAGE = "document_image"
    LIGHT_LOGO = "light_logo"
    DARK_LOGO = "dark_logo"
    NONE = "none"


class DocumentTableDensity(StrEnum):
    COMFORTABLE = "comfortable"
    COMPACT = "compact"


class DocumentAppearanceDraft(BaseModel):
    primary_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    heading_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    table_header_background: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    table_header_text: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    table_border_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    title_background_color: str = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    logo_source: DocumentLogoSource
    show_contacts: bool
    footer_text: str | None = Field(default=None, max_length=500)
    use_document_image_as_title_background: bool
    table_density: DocumentTableDensity


class DocumentAppearanceSettingsResponse(DocumentAppearanceDraft):
    version: int
    updated_at: datetime


class DocumentAppearanceSettingsUpdateRequest(DocumentAppearanceDraft):
    expected_version: int = Field(ge=1)


class DocumentAppearanceHistoryResponse(BaseModel):
    id: int
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
