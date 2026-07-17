import { apiClient } from "@/shared/api/client";

export type DocumentLogoSource =
  | "main_logo"
  | "document_image"
  | "light_logo"
  | "dark_logo"
  | "none";
export type DocumentTableDensity = "comfortable" | "compact";

export interface DocumentAppearanceDraft {
  primary_color: string;
  accent_color: string;
  heading_color: string;
  table_header_background: string;
  table_header_text: string;
  table_border_color: string;
  title_background_color: string;
  logo_source: DocumentLogoSource;
  show_contacts: boolean;
  footer_text: string | null;
  use_document_image_as_title_background: boolean;
  table_density: DocumentTableDensity;
}

export interface DocumentAppearanceSettings extends DocumentAppearanceDraft {
  version: number;
  updated_at: string;
}

export interface DocumentAppearanceSettingsUpdate extends DocumentAppearanceDraft {
  expected_version: number;
}

export interface DocumentAppearanceHistoryItem {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export async function getDocumentAppearanceSettings(): Promise<DocumentAppearanceSettings> {
  const response = await apiClient.get<DocumentAppearanceSettings>("/settings/documents");
  return response.data;
}

export async function updateDocumentAppearanceSettings(
  payload: DocumentAppearanceSettingsUpdate,
): Promise<DocumentAppearanceSettings> {
  const response = await apiClient.put<DocumentAppearanceSettings>("/settings/documents", payload);
  return response.data;
}

export async function getDocumentAppearanceHistory(
  limit = 20,
): Promise<DocumentAppearanceHistoryItem[]> {
  const response = await apiClient.get<DocumentAppearanceHistoryItem[]>(
    "/settings/documents/history",
    { params: { limit } },
  );
  return response.data;
}
