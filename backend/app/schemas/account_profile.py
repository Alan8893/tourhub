import re
from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.auth import UserRole

_PHONE_ALLOWED = re.compile(r"^[+0-9()\s.\-]+$")
_SOCIAL_HANDLE = re.compile(r"^[A-Za-z0-9_.-]{2,64}$")
_SOCIAL_CONFIG = {
    "telegram": (
        "t.me",
        {"t.me", "www.t.me", "telegram.me", "www.telegram.me"},
        "Telegram",
    ),
    "max": ("max.ru", {"max.ru", "www.max.ru"}, "MAX"),
    "vk": ("vk.com", {"vk.com", "www.vk.com", "vk.ru", "www.vk.ru"}, "VK"),
}


def normalize_display_name(value: str) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("Укажите ФИО.")
    if len(normalized) > 120:
        raise ValueError("ФИО не должно быть длиннее 120 символов.")
    return normalized


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if not _PHONE_ALLOWED.fullmatch(normalized):
        raise ValueError("Телефон может содержать только цифры и символы + ( ) - .")

    international = normalized.startswith("+") or normalized.startswith("00")
    digits = "".join(character for character in normalized if character.isdigit())
    if normalized.startswith("00"):
        digits = digits[2:]
    if not 7 <= len(digits) <= 15:
        raise ValueError("Укажите телефон длиной от 7 до 15 цифр.")
    return f"+{digits}" if international else digits


def normalize_social_link(value: str | None, platform: str) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None

    canonical_host, allowed_hosts, label = _SOCIAL_CONFIG[platform]
    candidate = normalized
    if candidate.startswith("@"):
        candidate = candidate[1:]

    lower_candidate = candidate.casefold()
    if "://" not in candidate and any(
        lower_candidate.startswith(f"{host}/") for host in allowed_hosts
    ):
        candidate = f"https://{candidate}"

    if "://" in candidate:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").casefold()
        if (
            parsed.scheme.casefold() != "https"
            or host not in allowed_hosts
            or parsed.username is not None
            or parsed.password is not None
            or parsed.port is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError(f"Укажите корректную HTTPS-ссылку на {label}.")
        handle = parsed.path.strip("/")
    else:
        handle = candidate.strip("/")

    if "/" in handle or not _SOCIAL_HANDLE.fullmatch(handle):
        raise ValueError(f"Укажите никнейм или ссылку на профиль {label}.")
    return f"https://{canonical_host}/{handle}"


class AccountProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str
    phone: str | None = None
    telegram_url: str | None = None
    max_url: str | None = None
    vk_url: str | None = None
    version: int = Field(ge=1)

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str) -> str:
        return normalize_display_name(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_phone(value)

    @field_validator("telegram_url")
    @classmethod
    def validate_telegram(cls, value: str | None) -> str | None:
        return normalize_social_link(value, "telegram")

    @field_validator("max_url")
    @classmethod
    def validate_max(cls, value: str | None) -> str | None:
        return normalize_social_link(value, "max")

    @field_validator("vk_url")
    @classmethod
    def validate_vk(cls, value: str | None) -> str | None:
        return normalize_social_link(value, "vk")


class PasswordChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=12, max_length=128)
    new_password: str = Field(min_length=12, max_length=128)
    new_password_confirm: str = Field(min_length=12, max_length=128)

    @model_validator(mode="after")
    def validate_passwords(self) -> "PasswordChangeRequest":
        if self.new_password != self.new_password_confirm:
            raise ValueError("Новый пароль и подтверждение не совпадают.")
        if self.new_password == self.current_password:
            raise ValueError("Новый пароль должен отличаться от текущего.")
        return self


class AccountProfileResponse(BaseModel):
    id: int
    email: str
    display_name: str
    phone: str | None
    telegram_url: str | None
    max_url: str | None
    vk_url: str | None
    role: UserRole
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime


class AccountSessionResponse(BaseModel):
    id: int
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    is_current: bool


class ClubContactResponse(BaseModel):
    id: int
    email: str
    display_name: str
    phone: str | None
    telegram_url: str | None
    max_url: str | None
    vk_url: str | None
    role: UserRole
    is_current: bool
