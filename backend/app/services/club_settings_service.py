import base64
import binascii
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
from typing import cast
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from PIL import Image, UnidentifiedImageError
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.engines.documents.branding import ClubBrandingDTO
from app.models.club_settings import ClubSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.club_settings import (
    ClubImageUpdate,
    ClubSettingsDetailUpdateRequest,
)

DEFAULT_CLUB_NAME = "TourHub"
LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200
MAX_IMAGE_PIXELS = 40_000_000
ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
EXPECTED_IMAGE_FORMATS = {
    "image/png": "PNG",
    "image/jpeg": "JPEG",
    "image/webp": "WEBP",
}


class SettingsVersionConflictError(Exception):
    pass


class ClubImageKind(StrEnum):
    MAIN_LOGO = "main_logo"
    LIGHT_LOGO = "light_logo"
    DARK_LOGO = "dark_logo"
    SQUARE_ICON = "square_icon"
    FAVICON = "favicon"
    LOGIN_BACKGROUND = "login_background"
    DOCUMENT_IMAGE = "document_image"


@dataclass(frozen=True)
class ImageRule:
    mime_attribute: str
    bytes_attribute: str
    max_bytes: int


IMAGE_RULES: dict[ClubImageKind, ImageRule] = {
    ClubImageKind.MAIN_LOGO: ImageRule("logo_mime_type", "logo_bytes", 2_000_000),
    ClubImageKind.LIGHT_LOGO: ImageRule(
        "light_logo_mime_type",
        "light_logo_bytes",
        2_000_000,
    ),
    ClubImageKind.DARK_LOGO: ImageRule(
        "dark_logo_mime_type",
        "dark_logo_bytes",
        2_000_000,
    ),
    ClubImageKind.SQUARE_ICON: ImageRule(
        "square_icon_mime_type",
        "square_icon_bytes",
        512_000,
    ),
    ClubImageKind.FAVICON: ImageRule(
        "favicon_mime_type",
        "favicon_bytes",
        512_000,
    ),
    ClubImageKind.LOGIN_BACKGROUND: ImageRule(
        "login_background_mime_type",
        "login_background_bytes",
        5_000_000,
    ),
    ClubImageKind.DOCUMENT_IMAGE: ImageRule(
        "document_image_mime_type",
        "document_image_bytes",
        5_000_000,
    ),
}


class ClubSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> ClubSettingsORM:
        settings = self.session.get(ClubSettingsORM, 1)
        if settings is not None:
            return settings

        settings = ClubSettingsORM(
            id=1,
            club_name=DEFAULT_CLUB_NAME,
            social_links=[],
            version=1,
        )
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(
        self,
        *,
        club_name: str,
        logo_data_url: str | None,
        remove_logo: bool,
    ) -> ClubSettingsORM:
        normalized_name = self._required_text(club_name, "Club name")
        if logo_data_url is not None and remove_logo:
            raise ValueError("Logo upload and removal cannot be requested together")

        settings = self.get()
        changed_fields: list[str] = []
        if settings.club_name != normalized_name:
            settings.club_name = normalized_name
            changed_fields.append("club_name")

        image_update = ClubImageUpdate(data_url=logo_data_url, remove=remove_logo)
        if self._apply_image_update(settings, ClubImageKind.MAIN_LOGO, image_update):
            changed_fields.append("images.main_logo")

        return self._commit_changes(settings, changed_fields)

    def update_details(
        self,
        request: ClubSettingsDetailUpdateRequest,
    ) -> ClubSettingsORM:
        settings = self.get()
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        normalized_values: dict[str, str | None] = {
            "club_name": self._required_text(request.club_name, "Club name"),
            "short_name": self._optional_text(request.short_name),
            "legal_name": self._optional_text(request.legal_name),
            "description": self._optional_text(request.description),
            "address": self._optional_text(request.address),
            "phone": self._optional_text(request.phone),
            "email": self._optional_text(request.email),
            "website": self._optional_text(request.website),
            "timezone": self._optional_text(request.timezone),
            "city": self._optional_text(request.city),
            "region": self._optional_text(request.region),
        }
        self._validate_email(normalized_values["email"])
        self._validate_url(normalized_values["website"], "Website")
        self._validate_timezone(normalized_values["timezone"])

        changed_fields: list[str] = []
        for field_name, value in normalized_values.items():
            if getattr(settings, field_name) != value:
                setattr(settings, field_name, value)
                changed_fields.append(field_name)

        normalized_social_links = self._normalize_social_links(request)
        if settings.social_links != normalized_social_links:
            settings.social_links = normalized_social_links
            changed_fields.append("social_links")

        image_updates = (
            (ClubImageKind.MAIN_LOGO, request.images.main_logo),
            (ClubImageKind.LIGHT_LOGO, request.images.light_logo),
            (ClubImageKind.DARK_LOGO, request.images.dark_logo),
            (ClubImageKind.SQUARE_ICON, request.images.square_icon),
            (ClubImageKind.FAVICON, request.images.favicon),
            (ClubImageKind.LOGIN_BACKGROUND, request.images.login_background),
            (ClubImageKind.DOCUMENT_IMAGE, request.images.document_image),
        )
        for image_kind, image_update in image_updates:
            if image_update is not None and self._apply_image_update(
                settings,
                image_kind,
                image_update,
            ):
                changed_fields.append(f"images.{image_kind.value}")

        return self._commit_changes(settings, changed_fields)

    def list_history(self, *, limit: int) -> Sequence[SystemSettingsHistoryORM]:
        statement = (
            select(SystemSettingsHistoryORM)
            .where(SystemSettingsHistoryORM.section == "club")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def to_branding(self) -> ClubBrandingDTO:
        settings = self.get()
        return ClubBrandingDTO(
            club_name=settings.club_name,
            logo_bytes=settings.logo_bytes,
            logo_mime_type=settings.logo_mime_type,
        )

    @staticmethod
    def logo_data_url(settings: ClubSettingsORM) -> str | None:
        return ClubSettingsService.image_data_url(settings, ClubImageKind.MAIN_LOGO)

    @staticmethod
    def image_data_url(
        settings: ClubSettingsORM,
        image_kind: ClubImageKind,
    ) -> str | None:
        rule = IMAGE_RULES[image_kind]
        image_bytes = cast(bytes | None, getattr(settings, rule.bytes_attribute))
        mime_type = cast(str | None, getattr(settings, rule.mime_attribute))
        if image_bytes is None or mime_type is None:
            return None
        encoded = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"

    def _commit_changes(
        self,
        settings: ClubSettingsORM,
        changed_fields: list[str],
    ) -> ClubSettingsORM:
        unique_changed_fields = list(dict.fromkeys(changed_fields))
        if not unique_changed_fields:
            return settings

        settings.version += 1
        self.session.add(
            SystemSettingsHistoryORM(
                section="club",
                actor_label=LOCAL_ADMIN_ACTOR,
                action="updated",
                changed_fields=unique_changed_fields,
                settings_version=settings.version,
            )
        )
        self.session.flush()
        self._trim_history()
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def _trim_history(self) -> None:
        stale_ids = self.session.scalars(
            select(SystemSettingsHistoryORM.id)
            .order_by(SystemSettingsHistoryORM.id.desc())
            .offset(HISTORY_LIMIT)
        ).all()
        if stale_ids:
            self.session.execute(
                delete(SystemSettingsHistoryORM).where(
                    SystemSettingsHistoryORM.id.in_(stale_ids)
                )
            )

    @staticmethod
    def _normalize_social_links(
        request: ClubSettingsDetailUpdateRequest,
    ) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for link in request.social_links:
            label = ClubSettingsService._required_text(link.label, "Social link label")
            url = ClubSettingsService._required_text(link.url, "Social link URL")
            ClubSettingsService._validate_url(url, "Social link")
            duplicate_key = (label.casefold(), url.casefold())
            if duplicate_key in seen:
                raise ValueError("Social links must be unique")
            seen.add(duplicate_key)
            normalized.append({"label": label, "url": url})
        return normalized

    @staticmethod
    def _apply_image_update(
        settings: ClubSettingsORM,
        image_kind: ClubImageKind,
        update: ClubImageUpdate,
    ) -> bool:
        if update.data_url is not None and update.remove:
            raise ValueError("Image upload and removal cannot be requested together")

        rule = IMAGE_RULES[image_kind]
        current_mime_type = cast(str | None, getattr(settings, rule.mime_attribute))
        current_bytes = cast(bytes | None, getattr(settings, rule.bytes_attribute))

        if update.remove:
            if current_mime_type is None and current_bytes is None:
                return False
            setattr(settings, rule.mime_attribute, None)
            setattr(settings, rule.bytes_attribute, None)
            return True

        if update.data_url is None:
            return False

        mime_type, image_bytes = ClubSettingsService._decode_image(
            update.data_url,
            max_bytes=rule.max_bytes,
        )
        if current_mime_type == mime_type and current_bytes == image_bytes:
            return False

        setattr(settings, rule.mime_attribute, mime_type)
        setattr(settings, rule.bytes_attribute, image_bytes)
        return True

    @staticmethod
    def _decode_image(data_url: str, *, max_bytes: int) -> tuple[str, bytes]:
        header, separator, payload = data_url.partition(",")
        if not separator or not header.startswith("data:") or not header.endswith(";base64"):
            raise ValueError("Image must be a base64 data URL")

        mime_type = header[5:-7]
        if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise ValueError("Image must be PNG, JPEG, or WebP")

        try:
            image_bytes = base64.b64decode(payload, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("Image contains invalid base64 data") from error

        if not image_bytes:
            raise ValueError("Image cannot be empty")
        if len(image_bytes) > max_bytes:
            raise ValueError(f"Image must not exceed {max_bytes // 1000} KB")

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                width, height = image.size
                image_format = image.format
                if width * height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image dimensions are too large")
                image.verify()
        except ValueError:
            raise
        except (
            UnidentifiedImageError,
            Image.DecompressionBombError,
            OSError,
            SyntaxError,
        ) as error:
            raise ValueError("Image is not valid") from error

        if image_format != EXPECTED_IMAGE_FORMATS[mime_type]:
            raise ValueError("Image content does not match its MIME type")

        return mime_type, image_bytes

    @staticmethod
    def _required_text(value: str, field_name: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty")
        return normalized

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _validate_email(value: str | None) -> None:
        if value is None:
            return
        local_part, separator, domain = value.rpartition("@")
        if not separator or not local_part or not domain or " " in value:
            raise ValueError("Email address is invalid")

    @staticmethod
    def _validate_url(value: str | None, field_name: str) -> None:
        if value is None:
            return
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"{field_name} must use an http or https URL")

    @staticmethod
    def _validate_timezone(value: str | None) -> None:
        if value is None:
            return
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError("Timezone must be a valid IANA timezone") from error
