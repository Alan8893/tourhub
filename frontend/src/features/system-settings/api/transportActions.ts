import { apiClient } from "@/shared/api/client";

export interface TransportActionResult {
  status: "sent" | "unavailable" | "failed";
  message: string;
  attempts: number;
  recipient: string | null;
}

export async function checkTransport(): Promise<TransportActionResult> {
  const response = await apiClient.post<TransportActionResult>("/settings/mail/check");
  return response.data;
}

export async function sendTestTransport(): Promise<TransportActionResult> {
  const response = await apiClient.post<TransportActionResult>("/settings/mail/test");
  return response.data;
}
