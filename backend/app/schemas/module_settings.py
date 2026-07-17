from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ModuleKey(StrEnum):
    PROJECTS = "projects"
    CATALOGUE = "catalogue"
    CATALOG_IMPORT = "catalog_import"
    SHOPPING = "shopping"
    EQUIPMENT = "equipment"
    DOCUMENTS = "documents"


class ModuleVisibilityDraft(BaseModel):
    projects_visible: bool
    catalogue_visible: bool
    catalog_import_visible: bool
    shopping_visible: bool
    equipment_visible: bool
    documents_visible: bool


class ModuleDefinitionResponse(BaseModel):
    key: ModuleKey
    label: str
    description: str
    visible: bool
    required: bool
    dependencies: list[ModuleKey]
    locked: bool
    lock_reason: str | None


class ModuleSettingsResponse(ModuleVisibilityDraft):
    version: int
    modules: list[ModuleDefinitionResponse]
    updated_at: datetime


class ModuleSettingsUpdateRequest(ModuleVisibilityDraft):
    expected_version: int = Field(ge=1)


class ModuleSettingsHistoryResponse(BaseModel):
    id: int
    actor_label: str
    action: str
    changed_fields: list[str]
    settings_version: int
    created_at: datetime
