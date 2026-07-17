import { apiClient } from "@/shared/api/client";

export interface ClubSettings {
  club_name: string;
  logo_data_url: string | null;
}

export interface ClubSettingsUpdate {
  club_name: string;
  logo_data_url: string | null;
  remove_logo: boolean;
}

export async function getClubSettings(): Promise<ClubSettings> {
  const response = await apiClient.get<ClubSettings>("/club-settings");
  return response.data;
}

export async function updateClubSettings(
  payload: ClubSettingsUpdate,
): Promise<ClubSettings> {
  const response = await apiClient.put<ClubSettings>("/club-settings", payload);
  return response.data;
}
