import { apiClient } from "@/shared/api/client";
import type { UserRole } from "@/features/auth/api/authApi";

export interface ManagedUser {
  id: number;
  email: string;
  display_name: string;
  role: UserRole;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
  last_login_at: string | null;
  is_current: boolean;
}

export interface ManagedUserUpdate {
  expected_version: number;
  role: UserRole;
  is_active: boolean;
}

export async function listManagedUsers(): Promise<ManagedUser[]> {
  const response = await apiClient.get<ManagedUser[]>("/users");
  return response.data;
}

export async function updateManagedUser(
  userId: number,
  payload: ManagedUserUpdate,
): Promise<ManagedUser> {
  const response = await apiClient.patch<ManagedUser>(`/users/${userId}`, payload);
  return response.data;
}
