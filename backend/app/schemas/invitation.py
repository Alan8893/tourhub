from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import normalize_email
from app.schemas.invitation_settings import InvitationDefaultRole
from app.schemas.mail_settings import MailDeliveryStatus


class InvitationStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    CONSUMED = "consumed"
    SUPERSEDED = "superseded"


class InvitationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    role: InvitationDefaultRole | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class InvitationListItemResponse(BaseModel):
    id: int
    email: str
    role: InvitationDefaultRole
    status: InvitationStatus
    created_at: datetime
    expires_at: datetime
    consumed_at: datetime | None
    revoked_at: datetime | None
    superseded_at: datetime | None


class InvitationCreatedResponse(InvitationListItemResponse):
    token: str
    acceptance_path: str
    delivery_status: MailDeliveryStatus
    delivery_message: str
    delivery_attempts: int = Field(ge=0)


class InvitationTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=32, max_length=512)

    @field_validator("token")
    @classmethod
    def normalize_token(cls, value: str) -> str:
        return value.strip()


class InvitationPublicResponse(BaseModel):
    email: str
    role: InvitationDefaultRole
    expires_at: datetime


class InvitationAcceptRequest(InvitationTokenRequest):
    display_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=12, max_length=128)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Укажите имя пользователя.")
        return normalized
