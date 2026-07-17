from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.module_settings import ModuleSettingsORM
from app.models.system_settings_history import SystemSettingsHistoryORM
from app.schemas.module_settings import (
    ModuleDefinitionResponse,
    ModuleKey,
    ModuleSettingsUpdateRequest,
)
from app.services.club_settings_service import SettingsVersionConflictError

LOCAL_ADMIN_ACTOR = "Локальный администратор"
HISTORY_LIMIT = 200


@dataclass(frozen=True)
class ModuleSpec:
    key: ModuleKey
    field_name: str
    label: str
    description: str
    required: bool = False
    dependencies: tuple[ModuleKey, ...] = ()


MODULE_SPECS: tuple[ModuleSpec, ...] = (
    ModuleSpec(
        ModuleKey.PROJECTS,
        "projects_visible",
        "Проекты",
        "Каталог походов и рабочее пространство подготовки.",
        required=True,
    ),
    ModuleSpec(
        ModuleKey.CATALOGUE,
        "catalogue_visible",
        "Каталог",
        "Блюда и рецепты, используемые меню и расчётами.",
        required=True,
    ),
    ModuleSpec(
        ModuleKey.CATALOG_IMPORT,
        "catalog_import_visible",
        "Импорт",
        "Загрузка и проверка каталогов через CSV.",
        dependencies=(ModuleKey.CATALOGUE,),
    ),
    ModuleSpec(
        ModuleKey.SHOPPING,
        "shopping_visible",
        "Закупка",
        "Раскладка, упаковки, список закупки и чек-лист.",
    ),
    ModuleSpec(
        ModuleKey.EQUIPMENT,
        "equipment_visible",
        "Оборудование",
        "Расчёт и ручная корректировка снаряжения проекта.",
    ),
    ModuleSpec(
        ModuleKey.DOCUMENTS,
        "documents_visible",
        "Документы",
        "PDF, Excel, печатная версия и ZIP проекта.",
        dependencies=(ModuleKey.SHOPPING, ModuleKey.EQUIPMENT),
    ),
)

DEFAULT_VALUES: dict[str, bool] = {
    spec.field_name: True for spec in MODULE_SPECS
}


class ModuleSettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> ModuleSettingsORM:
        settings = self.session.get(ModuleSettingsORM, 1)
        if settings is not None:
            return settings

        settings = ModuleSettingsORM(id=1, version=1, **DEFAULT_VALUES)
        self.session.add(settings)
        self.session.commit()
        self.session.refresh(settings)
        return settings

    def update(self, request: ModuleSettingsUpdateRequest) -> ModuleSettingsORM:
        self.get()
        settings = self.session.scalar(
            select(ModuleSettingsORM)
            .where(ModuleSettingsORM.id == 1)
            .with_for_update()
        )
        if settings is None:
            raise RuntimeError("Module settings singleton is missing")
        if settings.version != request.expected_version:
            raise SettingsVersionConflictError(
                f"Settings version {request.expected_version} is stale; current version is "
                f"{settings.version}"
            )

        normalized = {
            "projects_visible": request.projects_visible,
            "catalogue_visible": request.catalogue_visible,
            "catalog_import_visible": request.catalog_import_visible,
            "shopping_visible": request.shopping_visible,
            "equipment_visible": request.equipment_visible,
            "documents_visible": request.documents_visible,
        }
        self._validate(normalized)

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
                section="modules",
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

    def definitions(self, settings: ModuleSettingsORM) -> list[ModuleDefinitionResponse]:
        definitions: list[ModuleDefinitionResponse] = []
        for spec in MODULE_SPECS:
            lock_reason = self._lock_reason(spec, settings)
            definitions.append(
                ModuleDefinitionResponse(
                    key=spec.key,
                    label=spec.label,
                    description=spec.description,
                    visible=bool(getattr(settings, spec.field_name)),
                    required=spec.required,
                    dependencies=list(spec.dependencies),
                    locked=lock_reason is not None,
                    lock_reason=lock_reason,
                )
            )
        return definitions

    def list_history(self, *, limit: int) -> Sequence[SystemSettingsHistoryORM]:
        return self.session.scalars(
            select(SystemSettingsHistoryORM)
            .where(SystemSettingsHistoryORM.section == "modules")
            .order_by(SystemSettingsHistoryORM.id.desc())
            .limit(limit)
        ).all()

    @staticmethod
    def _validate(values: dict[str, bool]) -> None:
        if not values["projects_visible"]:
            raise ValueError("Модуль «Проекты» обязателен и не может быть скрыт.")
        if not values["catalogue_visible"]:
            raise ValueError("Модуль «Каталог» обязателен и не может быть скрыт.")
        if values["documents_visible"] and not values["shopping_visible"]:
            raise ValueError(
                "Модуль «Документы» требует видимый модуль «Закупка». "
                "Сначала скройте «Документы»."
            )
        if values["documents_visible"] and not values["equipment_visible"]:
            raise ValueError(
                "Модуль «Документы» требует видимый модуль «Оборудование». "
                "Сначала скройте «Документы»."
            )

    @staticmethod
    def _lock_reason(spec: ModuleSpec, settings: ModuleSettingsORM) -> str | None:
        if spec.required:
            return f"Модуль «{spec.label}» обязателен для текущего MVP."
        if spec.key is ModuleKey.SHOPPING and settings.documents_visible:
            return "Нельзя скрыть, пока виден модуль «Документы»."
        if spec.key is ModuleKey.EQUIPMENT and settings.documents_visible:
            return "Нельзя скрыть, пока виден модуль «Документы»."
        return None

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
