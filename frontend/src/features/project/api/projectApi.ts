import { apiClient } from "../../../api/client";

export interface Project {
  id: number;
  name: string;
  participants: number;
  days: number;
  start_date: string | null;
  first_meal: string | null;
  last_meal: string | null;
  status: string;
}

export interface ProjectListResponse {
  items: Project[];
}

export interface CreateProjectRequest {
  name: string;
  participants: number;
  days: number;
  start_date?: string;
  first_meal?: string;
  last_meal?: string;
}

export interface ProjectPreparationResponse {
  project_id: number;
  meal_plan_id: string;
  purchase_list_id: string;
  purchase_checklist_id: string;
}

export async function createProject(
  data: CreateProjectRequest,
): Promise<Project> {
  const response = await apiClient.post<Project>("/projects", data);

  return response.data;
}

export async function getProjects(): Promise<ProjectListResponse> {
  const response = await apiClient.get<ProjectListResponse>("/projects");
  return response.data;
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
