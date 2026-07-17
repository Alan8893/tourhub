import { apiClient } from "@/shared/api/client";

export type MailSecurityMode = "plain" | "starttls" | "tls";

export interface MailSettingsDraft {
  smtp_host: string;
  smtp_port: number;
  security_mode: MailSecurityMode;
  smtp_username: string | null;
  sender_email: string;
  sender_name: string;
  reply_to_email: string | null;
  test_recipient_email: string | null;
  timeout_seconds: number;
  retry_count: number;
}

export interface MailSettings extends MailSettingsDraft {
  version: number;
  updated_at: string;
  secret_configured: boolean;
  secret_source: "environment";
  secret_environment_variable: string;
  delivery_available: boolean;
  test_delivery_available: boolean;
}

export interface MailSettingsUpdate extends MailSettingsDraft {
  expected_version: number;
}

export interface MailSettingsHistoryItem {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

export const DEFAULT_MAIL_SETTINGS: MailSettings = {
  version: 1,
  smtp_host: "localhost",
  smtp_port: 587,
  security_mode: "starttls",
  smtp_username: null,
  sender_email: "tourhub@localhost",
  sender_name: "TourHub",
  reply_to_email: null,
  test_recipient_email: null,
  timeout_seconds: 30,
  retry_count: 3,
  updated_at: "",
  secret_configured: false,
  secret_source: "environment",
  secret_environment_variable: "TOURHUB_SMTP_SECRET",
  delivery_available: false,
  test_delivery_available: false,
};

export async function getMailSettings(): Promise<MailSettings> {
  const response = await apiClient.get<MailSettings>("/settings/mail");
  return response.data;
}

export async function updateMailSettings(payload: MailSettingsUpdate): Promise<MailSettings> {
  const response = await apiClient.put<MailSettings>("/settings/mail", payload);
  return response.data;
}

export async function getMailSettingsHistory(limit = 20): Promise<MailSettingsHistoryItem[]> {
  const response = await apiClient.get<MailSettingsHistoryItem[]>("/settings/mail/history", {
    params: { limit },
  });
  return response.data;
}
