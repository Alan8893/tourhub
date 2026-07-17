import axios from "axios";

import { apiClient } from "@/shared/api/client";

export type ClubImageKey =
  | "main_logo"
  | "light_logo"
  | "dark_logo"
  | "square_icon"
  | "favicon"
  | "login_background"
  | "document_image";

export interface ClubSocialLink {
  label: string;
  url: string;
}

export interface ClubImages {
  main_logo_data_url: string | null;
  light_logo_data_url: string | null;
  dark_logo_data_url: string | null;
  square_icon_data_url: string | null;
  favicon_data_url: string | null;
  login_background_data_url: string | null;
  document_image_data_url: string | null;
}

export interface ClubSettingsDetail {
  version: number;
  club_name: string;
  short_name: string | null;
  legal_name: string | null;
  description: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  timezone: string | null;
  city: string | null;
  region: string | null;
  social_links: ClubSocialLink[];
  images: ClubImages;
  updated_at: string;
}

export interface ClubImageUpdate {
  data_url: string | null;
  remove: boolean;
}

export interface ClubSettingsUpdate {
  expected_version: number;
  club_name: string;
  short_name: string | null;
  legal_name: string | null;
  description: string | null;
  address: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  timezone: string | null;
  city: string | null;
  region: string | null;
  social_links: ClubSocialLink[];
  images: Partial<Record<ClubImageKey, ClubImageUpdate>>;
}

export interface SystemSettingsHistoryItem {
  id: number;
  section: string;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export async function getSystemClubSettings(): Promise<ClubSettingsDetail> {
  const response = await apiClient.get<ClubSettingsDetail>("/settings/club");
  return response.data;
}

export async function updateSystemClubSettings(
  payload: ClubSettingsUpdate,
): Promise<ClubSettingsDetail> {
  try {
    const response = await apiClient.put<ClubSettingsDetail>("/settings/club", payload);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      const data = error.response.data as { error?: string; detail?: string };
      if (!data.detail && data.error) data.detail = data.error;
    }
    throw error;
  }
}

export async function getSystemSettingsHistory(
  limit = 20,
): Promise<SystemSettingsHistoryItem[]> {
  const response = await apiClient.get<SystemSettingsHistoryItem[]>("/settings/history", {
    params: { limit },
  });
  return response.data;
}
