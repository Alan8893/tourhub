import { apiClient } from "@/shared/api/client";
import type { UserRole } from "@/features/auth/api/authApi";

export interface AccountProfile {
  id: number;
  email: string;
  display_name: string;
  phone: string | null;
  telegram_url: string | null;
  max_url: string | null;
  vk_url: string | null;
  role: UserRole;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ClubContact {
  id: number;
  email: string;
  display_name: string;
  phone: string | null;
  telegram_url: string | null;
  max_url: string | null;
  vk_url: string | null;
  role: UserRole;
  is_current: boolean;
}

export interface AccountProfileUpdateInput {
  display_name: string;
  phone: string | null;
  telegram_url: string | null;
  max_url: string | null;
  vk_url: string | null;
  version: number;
}

export interface PasswordChangeInput {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

export async function getAccountProfile(): Promise<AccountProfile> {
  const response = await apiClient.get<AccountProfile>("/account");
  return response.data;
}

export async function updateAccountProfile(
  payload: AccountProfileUpdateInput,
): Promise<AccountProfile> {
  const response = await apiClient.patch<AccountProfile>("/account", payload);
  return response.data;
}

export async function changeAccountPassword(
  payload: PasswordChangeInput,
): Promise<AccountProfile> {
  const response = await apiClient.post<AccountProfile>("/account/password", payload);
  return response.data;
}

export async function getClubContacts(): Promise<ClubContact[]> {
  const response = await apiClient.get<ClubContact[]>("/account/contacts");
  return response.data;
}

export async function downloadContactVcard(userId: number): Promise<Blob> {
  const response = await apiClient.get<Blob>(`/account/contacts/${userId}/vcard`, {
    responseType: "blob",
  });
  return response.data;
}
