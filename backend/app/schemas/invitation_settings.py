import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class InvitationDefaultRole(StrEnum):
    INSTRUCTOR = "instructor"
    VERIFIED_INSTRUCTOR = "verified_instructor"


_DOMAIN_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_email_domains(values: list[str]) -> list[str]:
    if len(values) > 50:
        raise ValueError("Можно указать не более 50 разрешённых email-доменов.")

    normalized: set[str] = set()
    for raw_value in values:
        value = raw_value.strip().lower().rstrip(".")
        if not value:
            continue
        if any(marker in value for marker in ("@", "://", "/", "\\", ":")):
            raise ValueError(
                f"Домен «{raw_value}» должен быть указан без @, протокола, пути и порта."
            )
        if any(character.isspace() for character in value):
            raise ValueError(f"Домен «{raw_value}» не должен содержать пробелы.")

        try:
            ascii_domain = value.encode("idna").decode("ascii")
        except UnicodeError as error:
            raise ValueError(f"Домен «{raw_value}» имеет недопустимый формат.") from error

        if len(ascii_domain) > 253:
            raise ValueError(f"Домен «{raw_value}» превышает допустимую длину.")
        labels = ascii_domain.split(".")
        if any(not label or not _DOMAIN_LABEL.fullmatch(label) for label in labels):
            raise ValueError(
                f"Домен «{raw_value}» содержит недопустимые символы или дефисы."
            )
        normalized.add(ascii_domain)

    return sorted(normalized)


class InvitationPolicyDraft(BaseModel):
    expires_after_days: int = Field(ge=1, le=90)
    default_role: InvitationDefaultRole
    allowed_email_domains: list[str] = Field(default_factory=list)
    allow_resend: bool
    active_invitation_limit: int = Field(ge=1, le=1000)
    administrators_only: bool
    require_email_confirmation: bool

    @field_validator("allowed_email_domains")
    @classmethod
    def validate_domains(cls, values: list[str]) -> list[str]:
        return normalize_email_domains(values)

    @field_validator("administrators_only")
    @classmethod
    def validate_administrator_policy(cls, value: bool) -> bool:
        if not value:
            raise ValueError(
                "Управлять приглашениями могут только администраторы; это обязательное правило."
            )
        return value


class InvitationSettingsResponse(InvitationPolicyDraft):
    version: int
    updated_at: datetime


class InvitationSettingsUpdateRequest(InvitationPolicyDraft):
    expected_version: int = Field(ge=1)


class InvitationSettingsHistoryResponse(BaseModel):
    id: int
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
