from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AppearancePreset(StrEnum):
    TOURHUB = "tourhub"
    FOREST = "forest"
    OCEAN = "ocean"
    SUNSET = "sunset"
    CUSTOM = "custom"


class AppearanceFontFamily(StrEnum):
    SYSTEM = "system"
    MODERN = "modern"
    HUMANIST = "humanist"
    SERIF = "serif"


class AppearanceDensity(StrEnum):
    COMFORTABLE = "comfortable"
    COMPACT = "compact"


class AppearanceButtonStyle(StrEnum):
    CONTAINED = "contained"
    SOFT = "soft"
    OUTLINED = "outlined"


class AppearanceCardStyle(StrEnum):
    OUTLINED = "outlined"
    ELEVATED = "elevated"
    FLAT = "flat"


HexColor = str


class AppearanceColorTokens(BaseModel):
    primary: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    secondary: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    accent: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    background: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    paper: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    sidebar: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    appbar: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text_primary: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    text_secondary: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    divider: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    success: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    warning: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")
    error: HexColor = Field(pattern=r"^#[0-9A-Fa-f]{6}$")


class AppearanceThemeDraft(BaseModel):
    preset_name: AppearancePreset
    font_family: AppearanceFontFamily
    density: AppearanceDensity
    border_radius: int = Field(ge=0, le=24)
    button_style: AppearanceButtonStyle
    card_style: AppearanceCardStyle
    shadows_enabled: bool
    light: AppearanceColorTokens
    dark: AppearanceColorTokens


class AppearanceSettingsResponse(AppearanceThemeDraft):
    version: int
    updated_at: datetime


class AppearanceSettingsUpdateRequest(AppearanceThemeDraft):
    expected_version: int = Field(ge=1)


class AppearancePresetResponse(AppearanceThemeDraft):
    label: str


class AppearanceHistoryResponse(BaseModel):
    id: int
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
