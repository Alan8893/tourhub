import { apiClient } from "@/shared/api/client";

export type InvitationDefaultRole = "instructor" | "verified_instructor";

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
