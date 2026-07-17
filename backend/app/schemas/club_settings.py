from pydantic import BaseModel, Field


class ClubSettingsResponse(BaseModel):
    club_name: str
    logo_data_url: str | None


class ClubSettingsUpdateRequest(BaseModel):
    club_name: str = Field(min_length=1, max_length=255)
    logo_data_url: str | None = None
    remove_logo: bool = False
