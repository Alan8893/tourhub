from collections.abc import Sequence
from copy import deepcopy

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.appearance_settings import AppearanceSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.appearance_settings import (
    AppearanceColorTokens,
    AppearancePreset,
    AppearancePresetResponse,
    AppearanceSettingsUpdateRequest,
    AppearanceThemeDraft,
)
from app.services.club_settings_service import SettingsVersionConflictError

LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200
MIN_TEXT_CONTRAST = 4.5

TOURHUB_LIGHT = {
    "primary": "#1B5E20",
    "secondary": "#2E7D32",
    "accent": "#F9A825",
    "background": "#F4F7F4",
    "paper": "#FFFFFF",
    "sidebar": "#E8F2E8",
    "appbar": "#1B5E20",
    "text_primary": "#162018",
    "text_secondary": "#435348",
    "divider": "#C8D2CA",
    "success": "#2E7D32",
    "warning": "#ED6C02",
    "error": "#D32F2F",
}

TOURHUB_DARK = {
    "primary": "#81C784",
    "secondary": "#A5D6A7",
    "accent": "#FFD54F",
    "background": "#101713",
    "paper": "#18211B",
    "sidebar": "#1E2A22",
    "appbar": "#16351D",
    "text_primary": "#F2F7F3",
    "text_secondary": "#C1CDC4",
    "divider": "#405047",
    "success": "#81C784",
    "warning": "#FFB74D",
    "error": "#EF9A9A",
}

FOREST_LIGHT = {
    **TOURHUB_LIGHT,
    "primary": "#255D36",
    "secondary": "#517B45",
    "accent": "#B7791F",
    "background": "#F5F6EF",
    "sidebar": "#E7EBDD",
    "appbar": "#255D36",
}

FOREST_DARK = {
    **TOURHUB_DARK,
    "primary": "#8CCF9A",
    "secondary": "#B3D7A8",
    "accent": "#E9B96E",
    "background": "#111711",
    "paper": "#1A2219",
    "sidebar": "#222C20",
    "appbar": "#1D3C25",
}

OCEAN_LIGHT = {
    **TOURHUB_LIGHT,
    "primary": "#075985",
    "secondary": "#0369A1",
    "accent": "#0F766E",
    "background": "#F1F7FA",
    "sidebar": "#E1EFF5",
    "appbar": "#075985",
    "text_primary": "#10242E",
    "text_secondary": "#405D6B",
}

OCEAN_DARK = {
    **TOURHUB_DARK,
    "primary": "#7DD3FC",
    "secondary": "#BAE6FD",
    "accent": "#5EEAD4",
    "background": "#0B151B",
    "paper": "#13222B",
    "sidebar": "#172A35",
    "appbar": "#0C3A55",
}

SUNSET_LIGHT = {
    **TOURHUB_LIGHT,
    "primary": "#9A3412",
    "secondary": "#C2410C",
    "accent": "#A16207",
    "background": "#FFF7ED",
    "sidebar": "#FFEDD5",
    "appbar": "#9A3412",
    "text_primary": "#2F1B12",
    "text_secondary": "#6B4A3A",
}

SUNSET_DARK = {
    **TOURHUB_DARK,
    "primary": "#FDBA74",
    "secondary": "#FED7AA",
    "accent": "#FDE68A",
    "background": "#1A100C",
    "paper": "#261813",
    "sidebar": "#302019",
    "appbar": "#5C2410",
}

PRESETS: dict[AppearancePreset, tuple[str, dict[str, object]]] = {
    AppearancePreset.TOURHUB: (
        "TourHub",
        {
            "preset_name": AppearancePreset.TOURHUB,
            "font_family": "system",
            "density": "comfortable",
            "border_radius": 10,
            "button_style": "contained",
            "card_style": "outlined",
            "shadows_enabled": True,
            "light": TOURHUB_LIGHT,
            "dark": TOURHUB_DARK,
        },
    ),
    AppearancePreset.FOREST: (
        "Лес",
        {
            "preset_name": AppearancePreset.FOREST,
            "font_family": "humanist",
            "density": "comfortable",
            "border_radius": 12,
            "button_style": "soft",
            "card_style": "outlined",
            "shadows_enabled": False,
            "light": FOREST_LIGHT,
            "dark": FOREST_DARK,
        },
    ),
    AppearancePreset.OCEAN: (
        "Океан",
        {
            "preset_name": AppearancePreset.OCEAN,
            "font_family": "modern",
            "density": "comfortable",
            "border_radius": 8,
            "button_style": "contained",
            "card_style": "elevated",
            "shadows_enabled": True,
            "light": OCEAN_LIGHT,
            "dark": OCEAN_DARK,
        },
    ),
    AppearancePreset.SUNSET: (
        "Закат",
        {
            "preset_name": AppearancePreset.SUNSET,
            "font_family": "system",
            "density": "compact",
            "border_radius": 14,
            "button_style": "outlined",
            "card_style": "flat",
            "shadows_enabled": False,
            "light": SUNSET_LIGHT,
            "dark": SUNSET_DARK,
        },
    ),
}


class AppearanceSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> AppearanceSettingsORM:
        settings = self.session.get(AppearanceSettingsORM, 1)
        if settings is not None:
            return settings

        default = self.default_draft()
        settings = AppearanceSettingsORM(
            id=1,
            preset_name=default.preset_name.value,
            font_family=default.font_family.value,
            density=default.density.value,
            border_radius=default.border_radius,
            button_style=default.button_style.value,
            card_style=default.card_style.value,
            shadows_enabled=default.shadows_enabled,
            light_tokens=default.light.model_dump(),
            dark_tokens=default.dark.model_dump(),
            version=1,
        )
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(self, request: AppearanceSettingsUpdateRequest) -> AppearanceSettingsORM:
        self.get()
        settings = self.session.scalar(
            select(AppearanceSettingsORM)
            .where(AppearanceSettingsORM.id == 1)
            .with_for_update()
        )
        if settings is None:
            raise RuntimeError("Appearance settings singleton is missing")
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        light = self._normalize_tokens(request.light)
        dark = self._normalize_tokens(request.dark)
        self._validate_contrast("Светлая тема", light)
        self._validate_contrast("Тёмная тема", dark)

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
            if getattr(settings, field_name) != value:
                setattr(settings, field_name, value)
                changed_fields.append(field_name)

        changed_fields.extend(self._token_changes("light", settings.light_tokens, light))
        changed_fields.extend(self._token_changes("dark", settings.dark_tokens, dark))
        settings.light_tokens = light
        settings.dark_tokens = dark

        unique_changed_fields = list(dict.fromkeys(changed_fields))
        if not unique_changed_fields:
            return settings

        settings.version += 1
        self.session.add(
            SystemSettingsHistoryORM(
                section="appearance",
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

    def list_history(self, *, limit: int) -> Sequence[SystemSettingsHistoryORM]:
        return self.session.scalars(
            select(SystemSettingsHistoryORM)
            .where(SystemSettingsHistoryORM.section == "appearance")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        ).all()

    @staticmethod
    def default_draft() -> AppearanceThemeDraft:
        return AppearanceThemeDraft(**deepcopy(PRESETS[AppearancePreset.TOURHUB][1]))

    @staticmethod
    def presets() -> list[AppearancePresetResponse]:
        return [
            AppearancePresetResponse(label=label, **deepcopy(payload))
            for _, (label, payload) in PRESETS.items()
        ]

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
    def _normalize_tokens(tokens: AppearanceColorTokens) -> dict[str, str]:
        return {key: value.upper() for key, value in tokens.model_dump().items()}

    @staticmethod
    def _token_changes(
        prefix: str,
        current: dict[str, str],
        updated: dict[str, str],
    ) -> list[str]:
        return [
            f"{prefix}.{key}"
            for key, value in updated.items()
            if current.get(key) != value
        ]

    @classmethod
    def _validate_contrast(cls, theme_label: str, tokens: dict[str, str]) -> None:
        pairs = (
            ("основной текст", "text_primary", "фон приложения", "background"),
            ("основной текст", "text_primary", "фон карточек", "paper"),
            ("основной текст", "text_primary", "фон бокового меню", "sidebar"),
            ("вторичный текст", "text_secondary", "фон приложения", "background"),
            ("вторичный текст", "text_secondary", "фон карточек", "paper"),
            ("вторичный текст", "text_secondary", "фон бокового меню", "sidebar"),
        )
        for text_label, text_key, surface_label, surface_key in pairs:
            ratio = cls._contrast_ratio(tokens[text_key], tokens[surface_key])
            if ratio < MIN_TEXT_CONTRAST:
                raise ValueError(
                    f"{theme_label}: {text_label} {tokens[text_key]} имеет контраст "
                    f"{ratio:.2f}:1 с полем «{surface_label}» {tokens[surface_key]}; "
                    f"требуется не менее {MIN_TEXT_CONTRAST:.1f}:1."
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
