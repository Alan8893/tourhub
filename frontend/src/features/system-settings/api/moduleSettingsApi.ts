import { apiClient } from "@/shared/api/client";

export type ModuleKey =
  | "projects"
  | "catalogue"
  | "catalog_import"
  | "shopping"
  | "equipment"
  | "documents";

export interface ModuleVisibilityDraft {
  projects_visible: boolean;
  catalogue_visible: boolean;
  catalog_import_visible: boolean;
  shopping_visible: boolean;
  equipment_visible: boolean;
  documents_visible: boolean;
}

export interface ModuleDefinition {
  key: ModuleKey;
  label: string;
  description: string;
  visible: boolean;
  required: boolean;
  dependencies: ModuleKey[];
  locked: boolean;
  lock_reason: string | null;
}

export interface ModuleSettings extends ModuleVisibilityDraft {
  version: number;
  modules: ModuleDefinition[];
  updated_at: string;
}

export interface ModuleSettingsUpdate extends ModuleVisibilityDraft {
  expected_version: number;
}

export interface ModuleSettingsHistoryItem {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export const DEFAULT_MODULE_SETTINGS: ModuleSettings = {
  version: 1,
  projects_visible: true,
  catalogue_visible: true,
  catalog_import_visible: true,
  shopping_visible: true,
  equipment_visible: true,
  documents_visible: true,
  modules: [],
  updated_at: "",
};

export async function getModuleSettings(): Promise<ModuleSettings> {
  const response = await apiClient.get<ModuleSettings>("/settings/modules");
  return response.data;
}

export async function updateModuleSettings(
  payload: ModuleSettingsUpdate,
): Promise<ModuleSettings> {
  const response = await apiClient.put<ModuleSettings>("/settings/modules", payload);
  return response.data;
}

export async function getModuleSettingsHistory(
  limit = 20,
): Promise<ModuleSettingsHistoryItem[]> {
  const response = await apiClient.get<ModuleSettingsHistoryItem[]>("/settings/modules/history", {
    params: { limit },
  });
  return response.data;
}
