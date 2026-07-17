from collections.abc import Sequence
from typing import cast

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.engines.documents.branding import ClubBrandingDTO, DocumentPaletteDTO
from app.models.club_settings import ClubSettingsORM
from app.models.document_appearance_settings import DocumentAppearanceSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.document_appearance_settings import (
    DocumentAppearanceSettingsUpdateRequest,
    DocumentLogoSource,
)
from app.services.club_settings_service import SettingsVersionConflictError

LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200
MIN_TEXT_CONTRAST = 4.5

DEFAULT_VALUES: dict[str, object] = {
    "primary_color": "#1B5E20",
    "accent_color": "#F9A825",
    "heading_color": "#1B5E20",
    "table_header_background": "#E8F2E8",
    "table_header_text": "#162018",
    "table_border_color": "#405047",
    "title_background_color": "#F4F7F4",
    "logo_source": DocumentLogoSource.MAIN_LOGO.value,
    "show_contacts": True,
    "footer_text": None,
    "use_document_image_as_title_background": False,
    "table_density": "comfortable",
}


class DocumentAppearanceSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> DocumentAppearanceSettingsORM:
        settings = self.session.get(DocumentAppearanceSettingsORM, 1)
        if settings is not None:
            return settings

        settings = DocumentAppearanceSettingsORM(id=1, version=1, **DEFAULT_VALUES)
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(
        self,
        request: DocumentAppearanceSettingsUpdateRequest,
    ) -> DocumentAppearanceSettingsORM:
        self.get()
        settings = self.session.scalar(
            select(DocumentAppearanceSettingsORM)
            .where(DocumentAppearanceSettingsORM.id == 1)
            .with_for_update()
        )
        if settings is None:
            raise RuntimeError("Document appearance settings singleton is missing")
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        normalized: dict[str, object] = {
            "primary_color": request.primary_color.upper(),
            "accent_color": request.accent_color.upper(),
            "heading_color": request.heading_color.upper(),
            "table_header_background": request.table_header_background.upper(),
            "table_header_text": request.table_header_text.upper(),
            "table_border_color": request.table_border_color.upper(),
            "title_background_color": request.title_background_color.upper(),
            "logo_source": request.logo_source.value,
            "show_contacts": request.show_contacts,
            "footer_text": self._optional_text(request.footer_text),
            "use_document_image_as_title_background": (
                request.use_document_image_as_title_background
            ),
            "table_density": request.table_density.value,
        }
        self._validate_contrast(
            cast(str, normalized["table_header_text"]),
            cast(str, normalized["table_header_background"]),
        )

        changed_fields: list[str] = []
        for field_name, value in normalized.items():
            if getattr(settings, field_name) != value:
                setattr(settings, field_name, value)
                changed_fields.append(field_name)

        if not changed_fields:
            return settings

        settings.version += 1
        self.session.add(
            SystemSettingsHistoryORM(
                section="documents",
                actor_label=LOCAL_ADMIN_ACTOR,
                action="updated",
                changed_fields=changed_fields,
                settings_version=settings.version,
            )
        )
        self.session.flush()
        self._trim_history()
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def list_history(self, *, limit: int) -> Sequence[SystemSettingsHistoryORM]:
        return self.session.scalars(
            select(SystemSettingsHistoryORM)
            .where(SystemSettingsHistoryORM.section == "documents")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        ).all()

    def to_branding(self, club: ClubSettingsORM) -> ClubBrandingDTO:
        settings = self.get()
        logo_bytes, logo_mime_type = self._logo(club, settings.logo_source)
        title_background_bytes = (
            club.document_image_bytes
            if settings.use_document_image_as_title_background
            else None
        )
        title_background_mime_type = (
            club.document_image_mime_type
            if settings.use_document_image_as_title_background
            else None
        )
        return ClubBrandingDTO(
            club_name=club.club_name,
            logo_bytes=logo_bytes,
            logo_mime_type=logo_mime_type,
            contact_lines=self._contact_lines(club) if settings.show_contacts else (),
            footer_text=settings.footer_text,
            palette=DocumentPaletteDTO(
                primary_color=settings.primary_color,
                accent_color=settings.accent_color,
                heading_color=settings.heading_color,
                table_header_background=settings.table_header_background,
                table_header_text=settings.table_header_text,
                table_border_color=settings.table_border_color,
                title_background_color=settings.title_background_color,
            ),
            table_density=settings.table_density,
            title_background_bytes=title_background_bytes,
            title_background_mime_type=title_background_mime_type,
        )

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
    def _optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @staticmethod
    def _logo(club: ClubSettingsORM, source: str) -> tuple[bytes | None, str | None]:
        if source == DocumentLogoSource.NONE.value:
            return None, None

        attributes = {
            DocumentLogoSource.MAIN_LOGO.value: ("logo_bytes", "logo_mime_type"),
            DocumentLogoSource.DOCUMENT_IMAGE.value: (
                "document_image_bytes",
                "document_image_mime_type",
            ),
            DocumentLogoSource.LIGHT_LOGO.value: (
                "light_logo_bytes",
                "light_logo_mime_type",
            ),
            DocumentLogoSource.DARK_LOGO.value: (
                "dark_logo_bytes",
                "dark_logo_mime_type",
            ),
        }
        bytes_attribute, mime_attribute = attributes.get(
            source,
            attributes[DocumentLogoSource.MAIN_LOGO.value],
        )
        image_bytes = cast(bytes | None, getattr(club, bytes_attribute))
        mime_type = cast(str | None, getattr(club, mime_attribute))
        if image_bytes is not None and mime_type is not None:
            return image_bytes, mime_type
        return club.logo_bytes, club.logo_mime_type

    @staticmethod
    def _contact_lines(club: ClubSettingsORM) -> tuple[str, ...]:
        lines: list[str] = []
        locality = ", ".join(value for value in (club.city, club.region) if value)
        if locality:
            lines.append(locality)
        if club.address:
            lines.append(club.address)
        if club.phone:
            lines.append(f"Тел.: {club.phone}")
        if club.email:
            lines.append(f"Email: {club.email}")
        if club.website:
            lines.append(club.website)
        return tuple(lines)

    @classmethod
    def _validate_contrast(cls, foreground: str, background: str) -> None:
        ratio = cls._contrast_ratio(foreground, background)
        if ratio < MIN_TEXT_CONTRAST:
            raise ValueError(
                f"Текст заголовка таблицы {foreground} имеет контраст {ratio:.2f}:1 "
                f"с фоном {background}; требуется не менее {MIN_TEXT_CONTRAST:.1f}:1."
            )

    @classmethod
    def _contrast_ratio(cls, first: str, second: str) -> float:
        first_luminance = cls._relative_luminance(first)
        second_luminance = cls._relative_luminance(second)
        lighter = max(first_luminance, second_luminance)
        darker = min(first_luminance, second_luminance)
        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def _relative_luminance(color: str) -> float:
        channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]

        def linearize(channel: float) -> float:
            if channel <= 0.04045:
                return channel / 12.92
            return ((channel + 0.055) / 1.055) ** 2.4

        red, green, blue = (linearize(channel) for channel in channels)
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue
