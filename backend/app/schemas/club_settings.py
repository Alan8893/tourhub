from datetime import datetime

from pydantic import BaseModel, Field


class ClubSettingsResponse(BaseModel):
    club_name: str
    logo_data_url: str | None


class ClubSettingsUpdateRequest(BaseModel):
    club_name: str = Field(min_length=1, max_length=255)
    logo_data_url: str | None = None
    remove_logo: bool = False


class ClubSocialLink(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1, max_length=500)


class ClubImageUpdate(BaseModel):
    data_url: str | None = None
    remove: bool = False


class ClubImagesUpdate(BaseModel):
    main_logo: ClubImageUpdate | None = None
    light_logo: ClubImageUpdate | None = None
    dark_logo: ClubImageUpdate | None = None
    square_icon: ClubImageUpdate | None = None
    favicon: ClubImageUpdate | None = None
    login_background: ClubImageUpdate | None = None
    document_image: ClubImageUpdate | None = None


class ClubImagesResponse(BaseModel):
    main_logo_data_url: str | None
    light_logo_data_url: str | None
    dark_logo_data_url: str | None
    square_icon_data_url: str | None
    favicon_data_url: str | None
    login_background_data_url: str | None
    document_image_data_url: str | None


class ClubSettingsDetailResponse(BaseModel):
    version: int
    club_name: str
    short_name: str | None
    legal_name: str | None
    description: str | None
    address: str | None
    phone: str | None
    email: str | None
    website: str | None
    timezone: str | None
    city: str | None
    region: str | None
    social_links: list[ClubSocialLink]
    images: ClubImagesResponse
    updated_at: datetime


class ClubSettingsDetailUpdateRequest(BaseModel):
    expected_version: int = Field(ge=1)
    club_name: str = Field(min_length=1, max_length=255)
    short_name: str | None = Field(default=None, max_length=100)
    legal_name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=320)
    website: str | None = Field(default=None, max_length=500)
    timezone: str | None = Field(default=None, max_length=64)
    city: str | None = Field(default=None, max_length=255)
    region: str | None = Field(default=None, max_length=255)
    social_links: list[ClubSocialLink] = Field(default_factory=list, max_length=10)
    images: ClubImagesUpdate = Field(default_factory=ClubImagesUpdate)


class SystemSettingsHistoryResponse(BaseModel):
    id: int
    section: str
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
