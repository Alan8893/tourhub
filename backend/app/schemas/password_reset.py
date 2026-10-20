from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import normalize_email


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class PasswordResetConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=20, max_length=200)
    password: str = Field(min_length=12, max_length=128)


class PasswordResetRequestResponse(BaseModel):
    message: str


class PasswordResetConfirmResponse(BaseModel):
    message: str
