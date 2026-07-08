import { apiClient } from "../../../api/client";

export interface Project {
  id: number;
  name: string;
  participants: number;
  days: number;
  status: string;
}

export interface ProjectPreparationResponse {
  project_id: number;
  meal_plan_id: string;
  purchase_list_id: string;
  purchase_checklist_id: string;
}

export async function getProject(projectId: number): Promise<Project> {
  const response = await apiClient.get<Project>(
    `/projects/${projectId}`,
  );

  return response.data;
}

export async function prepareProject(
  projectId: number,
): Promise<ProjectPreparationResponse> {
  const response = await apiClient.post<ProjectPreparationResponse>(
    `/projects/${projectId}/prepare`,
  );

  return response.data;
}
