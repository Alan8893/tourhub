import axios from "axios";

export interface Project {
  id: number;
  name: string;
  participants: number;
  days: number;
  status: string;
}

export async function getProject(projectId: number): Promise<Project> {
  const response = await axios.get<Project>(
    `/api/v1/projects/${projectId}`,
  );

  return response.data;
}
