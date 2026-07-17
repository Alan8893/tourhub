import ipaddress
import re
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MailSecurityMode(StrEnum):
    PLAIN = "plain"
    STARTTLS = "starttls"
    TLS = "tls"


_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_EMAIL_LOCAL = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+$")


def normalize_smtp_host(raw_value: str) -> str:
    value = raw_value.strip().lower().rstrip(".")
    if not value:
        raise ValueError("SMTP host обязателен.")
    if any(character.isspace() for character in value):
        raise ValueError("SMTP host не должен содержать пробелы.")
    if any(marker in value for marker in ("@", "://", "/", "\\")):
        raise ValueError("SMTP host указывается без протокола, пользователя и пути.")

    candidate = value[1:-1] if value.startswith("[") and value.endswith("]") else value
    try:
        return ipaddress.ip_address(candidate).compressed
    except ValueError:
        pass

    if ":" in value:
        raise ValueError("Порт указывается в отдельном поле, не внутри SMTP host.")

    try:
        ascii_host = value.encode("idna").decode("ascii")
    except UnicodeError as error:
        raise ValueError("SMTP host имеет недопустимый формат.") from error

    if len(ascii_host) > 253:
        raise ValueError("SMTP host превышает допустимую длину.")
    labels = ascii_host.split(".")
    if any(not label or not _HOST_LABEL.fullmatch(label) for label in labels):
        raise ValueError("SMTP host содержит недопустимые символы или дефисы.")
    return ascii_host


def normalize_email(raw_value: str, *, field_name: str) -> str:
    value = raw_value.strip()
    if any(character.isspace() for character in value):
        raise ValueError(f"{field_name} не должен содержать пробелы.")
    if value.count("@") != 1:
        raise ValueError(f"{field_name} должен быть корректным email-адресом.")
    local_part, domain = value.rsplit("@", 1)
    if (
        not local_part
        or len(local_part) > 64
        or local_part.startswith(".")
        or local_part.endswith(".")
        or ".." in local_part
        or not _EMAIL_LOCAL.fullmatch(local_part)
    ):
        raise ValueError(f"{field_name} содержит недопустимую локальную часть.")
    normalized_domain = normalize_smtp_host(domain)
    normalized = f"{local_part}@{normalized_domain}"
    if len(normalized) > 320:
        raise ValueError(f"{field_name} превышает допустимую длину.")
    return normalized


def normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class MailSettingsDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    smtp_host: str = Field(min_length=1, max_length=253)
    smtp_port: int = Field(ge=1, le=65535)
    security_mode: MailSecurityMode
    smtp_username: str | None = Field(default=None, max_length=255)
    sender_email: str = Field(min_length=3, max_length=320)
    sender_name: str = Field(min_length=1, max_length=120)
    reply_to_email: str | None = Field(default=None, max_length=320)
    test_recipient_email: str | None = Field(default=None, max_length=320)
    timeout_seconds: int = Field(ge=1, le=120)
    retry_count: int = Field(ge=0, le=10)

    @field_validator("smtp_host")
    @classmethod
    def validate_smtp_host(cls, value: str) -> str:
        return normalize_smtp_host(value)

    @field_validator("smtp_username")
    @classmethod
    def validate_smtp_username(cls, value: str | None) -> str | None:
        return normalize_optional_text(value)

    @field_validator("sender_name")
    @classmethod
    def validate_sender_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Имя отправителя обязательно.")
        return normalized

    @field_validator("sender_email")
    @classmethod
    def validate_sender_email(cls, value: str) -> str:
        return normalize_email(value, field_name="Адрес отправителя")

    @field_validator("reply_to_email", "test_recipient_email", mode="before")
    @classmethod
    def normalize_optional_email_input(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("reply_to_email")
    @classmethod
    def validate_reply_to_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_email(value, field_name="Reply-To")

    @field_validator("test_recipient_email")
    @classmethod
    def validate_test_recipient_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_email(value, field_name="Тестовый адрес")


class MailSettingsResponse(MailSettingsDraft):
    version: int
    updated_at: datetime
    secret_configured: bool
    secret_source: Literal["environment"]
    secret_environment_variable: str
    delivery_available: bool
    test_delivery_available: bool


class MailSettingsUpdateRequest(MailSettingsDraft):
    expected_version: int = Field(ge=1)


class MailSettingsHistoryResponse(BaseModel):
    id: int
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
