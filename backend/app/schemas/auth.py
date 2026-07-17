import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class UserRole(StrEnum):
    ADMINISTRATOR = "administrator"
    INSTRUCTOR = "instructor"
    VERIFIED_INSTRUCTOR = "verified_instructor"


def normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) > 320 or not _EMAIL_PATTERN.fullmatch(normalized):
        raise ValueError("Укажите корректный email-адрес.")
    return normalized


class BootstrapStatusResponse(BaseModel):
    bootstrap_required: bool


class CredentialRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    password: str = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class BootstrapRequest(CredentialRequest):
    display_name: str = Field(min_length=1, max_length=120)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Укажите имя администратора.")
        return normalized


class LoginRequest(CredentialRequest):
    pass


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserResponse
