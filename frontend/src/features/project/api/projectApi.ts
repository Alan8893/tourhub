import { apiClient } from "../../../api/client";

export interface Project {
  id: number;
  name: string;
  participants: number;
  days: number;
  status: string;
}

export async function getProject(projectId: number): Promise<Project> {
  const response = await apiClient.get<Project>(
    `/projects/${projectId}`,
  );

  return response.data;
}
