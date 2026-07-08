export interface WorkflowStatusesResponse {
  purchase_list: string[];
  purchase_checklist: string[];
}

export interface MetaResponse {
  name: string;
  version: string;
  api_version: string;
  statuses: WorkflowStatusesResponse;
}
