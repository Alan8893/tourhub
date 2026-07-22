import type { UserRole } from "@/features/auth/api/authApi";
import { apiClient } from "@/shared/api/client";

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

export interface AccountSession {
  id: number;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
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

export async function getAccountSessions(): Promise<AccountSession[]> {
  const response = await apiClient.get<AccountSession[]>("/account/sessions");
  return response.data;
}

export async function revokeAccountSession(sessionId: number): Promise<void> {
  await apiClient.delete(`/account/sessions/${sessionId}`);
}
