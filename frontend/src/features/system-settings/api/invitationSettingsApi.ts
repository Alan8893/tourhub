import type { AuthUser } from "@/features/auth/api/authApi";
import { apiClient } from "@/shared/api/client";

export type InvitationDefaultRole = "instructor" | "verified_instructor";
export type InvitationStatus = "active" | "expired" | "revoked" | "consumed" | "superseded";
export type InvitationDeliveryStatus = "sent" | "unavailable" | "failed";

export interface InvitationPolicyDraft {
  expires_after_days: number;
  default_role: InvitationDefaultRole;
  allowed_email_domains: string[];
  allow_resend: boolean;
  active_invitation_limit: number;
  administrators_only: boolean;
  require_email_confirmation: boolean;
}

export interface InvitationSettings extends InvitationPolicyDraft {
  version: number;
  updated_at: string;
}

export interface InvitationSettingsUpdate extends InvitationPolicyDraft {
  expected_version: number;
}

export interface InvitationSettingsHistoryItem {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export interface InvitationRecord {
  id: number;
  email: string;
  role: InvitationDefaultRole;
  status: InvitationStatus;
  created_at: string;
  expires_at: string;
  consumed_at: string | null;
  revoked_at: string | null;
  superseded_at: string | null;
}

export interface InvitationCreated extends InvitationRecord {
  token: string;
  acceptance_path: string;
  delivery_status: InvitationDeliveryStatus;
  delivery_message: string;
  delivery_attempts: number;
}

export interface InvitationPublicInfo {
  email: string;
  role: InvitationDefaultRole;
  expires_at: string;
}

export const DEFAULT_INVITATION_SETTINGS: InvitationSettings = {
  version: 1,
  expires_after_days: 7,
  default_role: "instructor",
  allowed_email_domains: [],
  allow_resend: true,
  active_invitation_limit: 100,
  administrators_only: true,
  require_email_confirmation: true,
  updated_at: "",
};

export async function getInvitationSettings(): Promise<InvitationSettings> {
  const response = await apiClient.get<InvitationSettings>("/settings/invitations");
  return response.data;
}

export async function updateInvitationSettings(
  payload: InvitationSettingsUpdate,
): Promise<InvitationSettings> {
  const response = await apiClient.put<InvitationSettings>("/settings/invitations", payload);
  return response.data;
}

export async function getInvitationSettingsHistory(
  limit = 20,
): Promise<InvitationSettingsHistoryItem[]> {
  const response = await apiClient.get<InvitationSettingsHistoryItem[]>(
    "/settings/invitations/history",
    { params: { limit } },
  );
  return response.data;
}

export async function listInvitations(limit = 100): Promise<InvitationRecord[]> {
  const response = await apiClient.get<InvitationRecord[]>("/invitations", {
    params: { limit },
  });
  return response.data;
}

export async function createInvitation(payload: {
  email: string;
  role?: InvitationDefaultRole;
}): Promise<InvitationCreated> {
  const response = await apiClient.post<InvitationCreated>("/invitations", payload);
  return response.data;
}

export async function reissueInvitation(id: number): Promise<InvitationCreated> {
  const response = await apiClient.post<InvitationCreated>(`/invitations/${id}/reissue`);
  return response.data;
}

export async function revokeInvitation(id: number): Promise<InvitationRecord> {
  const response = await apiClient.post<InvitationRecord>(`/invitations/${id}/revoke`);
  return response.data;
}

export async function inspectInvitation(token: string): Promise<InvitationPublicInfo> {
  const response = await apiClient.post<InvitationPublicInfo>("/invitations/inspect", { token });
  return response.data;
}

export async function acceptInvitation(payload: {
  token: string;
  display_name: string;
  password: string;
}): Promise<AuthUser> {
  const response = await apiClient.post<{ user: AuthUser }>("/invitations/accept", payload);
  return response.data.user;
}
