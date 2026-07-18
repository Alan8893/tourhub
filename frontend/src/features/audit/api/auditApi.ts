import { apiClient } from "@/shared/api/client";

export interface AuditEvent {
  id: number;
  actor_user_id: number | null;
  actor_display_name: string;
  actor_email: string;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  before_data: Record<string, unknown> | null;
  after_data: Record<string, unknown> | null;
  context_data: Record<string, unknown>;
  created_at: string;
}

export interface AuditEventListResponse {
  items: AuditEvent[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditEventFilters {
  actor_user_id?: number;
  entity_type?: string;
  entity_id?: string;
  action?: string;
  created_from?: string;
  created_to?: string;
  limit?: number;
  offset?: number;
}

export async function getAuditEvents(
  filters: AuditEventFilters = {},
): Promise<AuditEventListResponse> {
  const response = await apiClient.get<AuditEventListResponse>("/audit/events", {
    params: filters,
  });
  return response.data;
}
