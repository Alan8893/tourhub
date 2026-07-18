from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import UserRole


class UserAdministrationResponse(BaseModel):
    id: int
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    is_current: bool


class UserAdministrationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    role: UserRole
    is_active: bool
