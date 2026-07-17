import { apiClient } from "@/shared/api/client";

export type AppearancePresetName = "tourhub" | "forest" | "ocean" | "sunset" | "custom";
export type AppearanceFontFamily = "system" | "modern" | "humanist" | "serif";
export type AppearanceDensity = "comfortable" | "compact";
export type AppearanceButtonStyle = "contained" | "soft" | "outlined";
export type AppearanceCardStyle = "outlined" | "elevated" | "flat";
export type DisplayModePreference = "system" | "light" | "dark";
export type ResolvedDisplayMode = "light" | "dark";

export interface AppearanceColorTokens {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  paper: string;
  sidebar: string;
  appbar: string;
  text_primary: string;
  text_secondary: string;
  divider: string;
  success: string;
  warning: string;
  error: string;
}

export interface AppearanceThemeDraft {
  preset_name: AppearancePresetName;
  font_family: AppearanceFontFamily;
  density: AppearanceDensity;
  border_radius: number;
  button_style: AppearanceButtonStyle;
  card_style: AppearanceCardStyle;
  shadows_enabled: boolean;
  light: AppearanceColorTokens;
  dark: AppearanceColorTokens;
}

export interface AppearanceSettings extends AppearanceThemeDraft {
  version: number;
  updated_at: string;
}

export interface AppearanceSettingsUpdate extends AppearanceThemeDraft {
  expected_version: number;
}

export interface AppearancePresetDefinition extends AppearanceThemeDraft {
  label: string;
}

export interface AppearanceHistoryItem {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export interface AppearanceThemeExport {
  schema: "tourhub-appearance-theme";
  schema_version: 1;
  exported_at: string;
  theme: AppearanceThemeDraft;
}

export async function getAppearanceSettings(): Promise<AppearanceSettings> {
  const response = await apiClient.get<AppearanceSettings>("/settings/appearance");
  return response.data;
}

export async function updateAppearanceSettings(
  payload: AppearanceSettingsUpdate,
): Promise<AppearanceSettings> {
  const response = await apiClient.put<AppearanceSettings>("/settings/appearance", payload);
  return response.data;
}

export async function getAppearancePresets(): Promise<AppearancePresetDefinition[]> {
  const response = await apiClient.get<AppearancePresetDefinition[]>(
    "/settings/appearance/presets",
  );
  return response.data;
}

export async function getAppearanceHistory(limit = 20): Promise<AppearanceHistoryItem[]> {
  const response = await apiClient.get<AppearanceHistoryItem[]>(
    "/settings/appearance/history",
    { params: { limit } },
  );
  return response.data;
}
