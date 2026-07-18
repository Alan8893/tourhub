import { apiClient } from "@/shared/api/client";

import type { RecipeGenerationMode } from "../model/recipeGenerationMode";

export interface Project {
  id: number;
  name: string;
  participants: number;
  days: number;
  start_date: string | null;
  first_meal: string | null;
  last_meal: string | null;
  recipe_generation_mode: RecipeGenerationMode;
  status: string;
}

export interface ProjectListResponse { items: Project[]; }

export interface CreateProjectRequest {
  name: string;
  participants: number;
  days: number;
  start_date?: string;
  first_meal?: string;
  last_meal?: string;
  recipe_generation_mode?: RecipeGenerationMode;
}

export interface ProjectPreparationResponse {
  project_id: number;
  meal_plan_id: string;
  purchase_list_id: string;
  purchase_checklist_id: string;
  equipment_list_id: string;
}

export async function createProject(data: CreateProjectRequest): Promise<Project> {
  return (await apiClient.post<Project>("/projects", data)).data;
}

export async function getProjects(): Promise<ProjectListResponse> {
  return (await apiClient.get<ProjectListResponse>("/projects")).data;
}

export async function getProject(projectId: number): Promise<Project> {
  return (await apiClient.get<Project>("/projects/" + projectId)).data;
}

export async function updateProjectRecipeGenerationMode(
  projectId: number,
  recipeGenerationMode: RecipeGenerationMode,
): Promise<Project> {
  return (
    await apiClient.patch<Project>(`/projects/${projectId}/recipe-generation-mode`, {
      recipe_generation_mode: recipeGenerationMode,
    })
  ).data;
}

export async function getProjectPreparation(
  projectId: number,
): Promise<ProjectPreparationResponse> {
  return (
    await apiClient.get<ProjectPreparationResponse>(
      "/projects/" + projectId + "/preparation",
    )
  ).data;
}

export async function prepareProject(
  projectId: number,
): Promise<ProjectPreparationResponse> {
  return (
    await apiClient.post<ProjectPreparationResponse>(
      "/projects/" + projectId + "/prepare",
    )
  ).data;
}
