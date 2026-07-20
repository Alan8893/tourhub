from dataclasses import dataclass
from typing import cast

from sqlalchemy.orm import Session

from app.models.appearance_settings import AppearanceSettingsORM
from app.models.club_settings import ClubSettingsORM
from app.models.document_appearance_settings import DocumentAppearanceSettingsORM
from app.models.invitation_settings import InvitationSettingsORM
from app.models.mail_settings import MailSettingsORM
from app.models.module_settings import ModuleSettingsORM
from app.models.user import UserORM
from app.schemas.appearance_settings import AppearanceSettingsUpdateRequest
from app.schemas.club_settings import ClubImageUpdate, ClubSettingsDetailUpdateRequest
from app.schemas.document_appearance_settings import (
    DocumentAppearanceSettingsUpdateRequest,
)
from app.schemas.invitation_settings import InvitationSettingsUpdateRequest
from app.schemas.mail_settings import MailSettingsUpdateRequest
from app.schemas.module_settings import ModuleSettingsUpdateRequest
from app.services.appearance_settings_service import AppearanceSettingsService
from app.services.audit_service import AuditService
from app.services.club_settings_service import (
    IMAGE_RULES,
    ClubImageKind,
    ClubSettingsService,
    SettingsVersionConflictError,
)
from app.services.document_appearance_settings_service import (
    DocumentAppearanceSettingsService,
)
from app.services.module_settings_service import ModuleSettingsService


@dataclass(frozen=True)
class SettingsAuditPlan:
    action: str
    section: str
    before: dict[str, object]
    after: dict[str, object]
    changed_fields: tuple[str, ...]
    previous_version: int
    settings_version: int


class SettingsAuditService:
    def __init__(self, session: Session, actor: UserORM) -> None:
        self.session = session
        self.actor = actor

    def stage(self, plan: SettingsAuditPlan) -> bool:
        if not plan.changed_fields:
            return False
        AuditService(self.session).record(
            actor=self.actor,
            action=plan.action,
            entity_type="system_settings",
            entity_id=plan.section,
            before=plan.before,
            after=plan.after,
            context={
                "section": plan.section,
                "changed_fields": list(plan.changed_fields),
                "previous_version": plan.previous_version,
                "settings_version": plan.settings_version,
            },
        )
        return True

    def record_mail_operation(
        self,
        *,
        action: str,
        settings: MailSettingsORM,
        status: str,
        attempts: int,
        recipient: str | None = None,
    ) -> None:
        outcome: dict[str, object] = {
            "status": status,
            "attempts": attempts,
        }
        if recipient is not None:
            outcome["recipient"] = recipient
        AuditService(self.session).record(
            actor=self.actor,
            action=action,
            entity_type="mail",
            entity_id="smtp",
            after=outcome,
            context={
                "settings_version": settings.version,
                "security_mode": settings.security_mode,
                "authentication_configured": bool(settings.smtp_username),
            },
        )
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    @classmethod
    def plan_legacy_club_update(
        cls,
        service: ClubSettingsService,
        settings: ClubSettingsORM,
        *,
        club_name: str,
        logo_data_url: str | None,
        remove_logo: bool,
    ) -> SettingsAuditPlan:
        normalized_name = service._required_text(club_name, "Club name")
        if logo_data_url is not None and remove_logo:
            raise ValueError("Logo upload and removal cannot be requested together")

        current: dict[str, object] = {"club_name": settings.club_name}
        updated: dict[str, object] = {"club_name": normalized_name}
        changed_fields: list[str] = []
        if settings.club_name != normalized_name:
            changed_fields.append("club_name")

        image_update = ClubImageUpdate(data_url=logo_data_url, remove=remove_logo)
        image_change = cls._planned_image_change(
            service,
            settings,
            ClubImageKind.MAIN_LOGO,
            image_update,
        )
        if image_change is not None:
            field_name = "images.main_logo"
            before_image, after_image = image_change
            current[field_name] = before_image
            updated[field_name] = after_image
            changed_fields.append(field_name)

        return cls._plan(
            action="club_settings_updated",
            section="club",
            version=settings.version,
            current=current,
            updated=updated,
            changed_fields=changed_fields,
        )

    @classmethod
    def plan_club_update(
        cls,
        service: ClubSettingsService,
        settings: ClubSettingsORM,
        request: ClubSettingsDetailUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
        normalized_values: dict[str, object] = {
            "club_name": service._required_text(request.club_name, "Club name"),
            "short_name": service._optional_text(request.short_name),
            "legal_name": service._optional_text(request.legal_name),
            "description": service._optional_text(request.description),
            "address": service._optional_text(request.address),
            "phone": service._optional_text(request.phone),
            "email": service._optional_text(request.email),
            "website": service._optional_text(request.website),
            "timezone": service._optional_text(request.timezone),
            "city": service._optional_text(request.city),
            "region": service._optional_text(request.region),
        }
        service._validate_email(cast(str | None, normalized_values["email"]))
        service._validate_url(
            cast(str | None, normalized_values["website"]),
            "Website",
        )
        service._validate_timezone(cast(str | None, normalized_values["timezone"]))

        current: dict[str, object] = {}
        updated: dict[str, object] = {}
        changed_fields: list[str] = []
        for field_name, value in normalized_values.items():
            current_value = cast(object, getattr(settings, field_name))
            current[field_name] = current_value
            updated[field_name] = value
            if current_value != value:
                changed_fields.append(field_name)

        normalized_social_links = service._normalize_social_links(request)
        current["social_links"] = settings.social_links
        updated["social_links"] = normalized_social_links
        if settings.social_links != normalized_social_links:
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
            if image_update is None:
                continue
            image_change = cls._planned_image_change(
                service,
                settings,
                image_kind,
                image_update,
            )
            if image_change is None:
                continue
            field_name = f"images.{image_kind.value}"
            before_image, after_image = image_change
            current[field_name] = before_image
            updated[field_name] = after_image
            changed_fields.append(field_name)

        return cls._plan(
            action="club_settings_updated",
            section="club",
            version=settings.version,
            current=current,
            updated=updated,
            changed_fields=changed_fields,
        )

    @classmethod
    def plan_appearance_update(
        cls,
        settings: AppearanceSettingsORM,
        request: AppearanceSettingsUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
        light = AppearanceSettingsService._normalize_tokens(request.light)
        dark = AppearanceSettingsService._normalize_tokens(request.dark)
        AppearanceSettingsService._validate_contrast("Светлая тема", light)
        AppearanceSettingsService._validate_contrast("Тёмная тема", dark)

        current: dict[str, object] = {}
        updated: dict[str, object] = {}
        changed_fields: list[str] = []
        scalar_values: dict[str, object] = {
            "preset_name": request.preset_name.value,
            "font_family": request.font_family.value,
            "density": request.density.value,
            "border_radius": request.border_radius,
            "button_style": request.button_style.value,
            "card_style": request.card_style.value,
            "shadows_enabled": request.shadows_enabled,
        }
        for field_name, value in scalar_values.items():
            current_value = cast(object, getattr(settings, field_name))
            current[field_name] = current_value
            updated[field_name] = value
            if current_value != value:
                changed_fields.append(field_name)

        for prefix, current_tokens, updated_tokens in (
            ("light", settings.light_tokens, light),
            ("dark", settings.dark_tokens, dark),
        ):
            for key, value in updated_tokens.items():
                field_name = f"{prefix}.{key}"
                current_value = current_tokens.get(key)
                current[field_name] = current_value
                updated[field_name] = value
                if current_value != value:
                    changed_fields.append(field_name)

        return cls._plan(
            action="appearance_settings_updated",
            section="appearance",
            version=settings.version,
            current=current,
            updated=updated,
            changed_fields=changed_fields,
        )

    @classmethod
    def plan_document_update(
        cls,
        settings: DocumentAppearanceSettingsORM,
        request: DocumentAppearanceSettingsUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
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
            "footer_text": DocumentAppearanceSettingsService._optional_text(
                request.footer_text
            ),
            "use_document_image_as_title_background": (
                request.use_document_image_as_title_background
            ),
            "table_density": request.table_density.value,
        }
        DocumentAppearanceSettingsService._validate_contrast(
            cast(str, normalized["table_header_text"]),
            cast(str, normalized["table_header_background"]),
        )
        return cls._simple_plan(
            action="document_appearance_settings_updated",
            section="documents",
            settings=settings,
            normalized=normalized,
        )

    @classmethod
    def plan_module_update(
        cls,
        settings: ModuleSettingsORM,
        request: ModuleSettingsUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
        normalized = {
            "projects_visible": request.projects_visible,
            "catalogue_visible": request.catalogue_visible,
            "catalog_import_visible": request.catalog_import_visible,
            "shopping_visible": request.shopping_visible,
            "equipment_visible": request.equipment_visible,
            "documents_visible": request.documents_visible,
        }
        ModuleSettingsService._validate(normalized)
        return cls._simple_plan(
            action="module_settings_updated",
            section="modules",
            settings=settings,
            normalized=normalized,
        )

    @classmethod
    def plan_invitation_update(
        cls,
        settings: InvitationSettingsORM,
        request: InvitationSettingsUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
        normalized: dict[str, object] = {
            "expires_after_days": request.expires_after_days,
            "default_role": request.default_role.value,
            "allowed_email_domains": list(request.allowed_email_domains),
            "allow_resend": request.allow_resend,
            "active_invitation_limit": request.active_invitation_limit,
            "administrators_only": request.administrators_only,
            "require_email_confirmation": request.require_email_confirmation,
        }
        return cls._simple_plan(
            action="invitation_settings_updated",
            section="invitations",
            settings=settings,
            normalized=normalized,
        )

    @classmethod
    def plan_mail_update(
        cls,
        settings: MailSettingsORM,
        request: MailSettingsUpdateRequest,
    ) -> SettingsAuditPlan:
        cls._ensure_version(settings.version, request.expected_version)
        normalized: dict[str, object] = {
            "smtp_host": request.smtp_host,
            "smtp_port": request.smtp_port,
            "security_mode": request.security_mode.value,
            "smtp_username": request.smtp_username,
            "sender_email": request.sender_email,
            "sender_name": request.sender_name,
            "reply_to_email": request.reply_to_email,
            "test_recipient_email": request.test_recipient_email,
            "timeout_seconds": request.timeout_seconds,
            "retry_count": request.retry_count,
        }
        return cls._simple_plan(
            action="mail_settings_updated",
            section="mail",
            settings=settings,
            normalized=normalized,
        )

    @classmethod
    def _simple_plan(
        cls,
        *,
        action: str,
        section: str,
        settings: object,
        normalized: dict[str, object],
    ) -> SettingsAuditPlan:
        current: dict[str, object] = {}
        changed_fields: list[str] = []
        for field_name, value in normalized.items():
            current_value = cast(object, getattr(settings, field_name))
            current[field_name] = current_value
            if current_value != value:
                changed_fields.append(field_name)
        version = cast(int, getattr(settings, "version"))
        return cls._plan(
            action=action,
            section=section,
            version=version,
            current=current,
            updated=normalized,
            changed_fields=changed_fields,
        )

    @staticmethod
    def _plan(
        *,
        action: str,
        section: str,
        version: int,
        current: dict[str, object],
        updated: dict[str, object],
        changed_fields: list[str],
    ) -> SettingsAuditPlan:
        unique_changed_fields = tuple(dict.fromkeys(changed_fields))
        before: dict[str, object] = {"version": version}
        after: dict[str, object] = {"version": version + 1}
        for field_name in unique_changed_fields:
            before[field_name] = current[field_name]
            after[field_name] = updated[field_name]
        return SettingsAuditPlan(
            action=action,
            section=section,
            before=before,
            after=after,
            changed_fields=unique_changed_fields,
            previous_version=version,
            settings_version=version + 1,
        )

    @staticmethod
    def _ensure_version(current_version: int, expected_version: int) -> None:
        if current_version != expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {expected_version} is stale; current version is "
                f"{current_version}"
            )

    @staticmethod
    def _image_snapshot(
        image_bytes: bytes | None,
        mime_type: str | None,
    ) -> dict[str, object]:
        return {
            "configured": image_bytes is not None and mime_type is not None,
            "mime_type": mime_type,
            "size_bytes": len(image_bytes) if image_bytes is not None else 0,
        }

    @classmethod
    def _planned_image_change(
        cls,
        service: ClubSettingsService,
        settings: ClubSettingsORM,
        image_kind: ClubImageKind,
        update: ClubImageUpdate,
    ) -> tuple[dict[str, object], dict[str, object]] | None:
        if update.data_url is not None and update.remove:
            raise ValueError("Image upload and removal cannot be requested together")

        rule = IMAGE_RULES[image_kind]
        current_mime_type = cast(str | None, getattr(settings, rule.mime_attribute))
        current_bytes = cast(bytes | None, getattr(settings, rule.bytes_attribute))
        before = cls._image_snapshot(current_bytes, current_mime_type)

        if update.remove:
            if current_mime_type is None and current_bytes is None:
                return None
            return before, cls._image_snapshot(None, None)
        if update.data_url is None:
            return None

        mime_type, image_bytes = service._decode_image(
            update.data_url,
            max_bytes=rule.max_bytes,
        )
        if current_mime_type == mime_type and current_bytes == image_bytes:
            return None
        return before, cls._image_snapshot(image_bytes, mime_type)
