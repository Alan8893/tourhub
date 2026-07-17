import { apiClient } from "@/shared/api/client";

export type UserRole = "administrator" | "instructor" | "verified_instructor";

export interface AuthUser {
  id: number;
  email: string;
  display_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  user: AuthUser;
}

export async function getBootstrapStatus(): Promise<boolean> {
  const response = await apiClient.get<{ bootstrap_required: boolean }>(
    "/auth/bootstrap-status",
  );
  return response.data.bootstrap_required;
}

export async function bootstrapAdministrator(payload: {
  email: string;
  display_name: string;
  password: string;
}): Promise<AuthUser> {
  const response = await apiClient.post<AuthResponse>("/auth/bootstrap", payload);
  return response.data.user;
}

export async function login(payload: {
  email: string;
  password: string;
}): Promise<AuthUser> {
  const response = await apiClient.post<AuthResponse>("/auth/login", payload);
  return response.data.user;
}

export async function getCurrentUser(): Promise<AuthUser | null> {
  try {
    const response = await apiClient.get<AuthResponse>("/auth/me");
    return response.data.user;
  } catch {
    return null;
  }
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
}
