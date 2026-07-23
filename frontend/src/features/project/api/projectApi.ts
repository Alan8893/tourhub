import type { UserRole } from "@/features/auth/api/authApi";
import { apiClient } from "@/shared/api/client";

import type { RecipeGenerationMode } from "../model/recipeGenerationMode";

export interface ProjectCapabilities {
  can_view: boolean;
  can_manage_project: boolean;
  can_manage_team: boolean;
  can_transfer_ownership: boolean;
  can_edit_menu: boolean;
  can_operate_shopping: boolean;
  can_operate_equipment: boolean;
  can_generate_documents: boolean;
  can_delete: boolean;
}

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
  owner_user_id: number | null;
  owner_display_name: string | null;
  capabilities: ProjectCapabilities | null;
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

export interface ProjectCopyResponse {
  project_id: number;
  meal_plan_id: string;
  copied_slot_count: number;
  copied_assignment_count: number;
  skipped_assignment_count: number;
  warnings: string[];
}

export interface ProjectPreparationResponse {
  project_id: number;
  meal_plan_id: string;
  purchase_list_id: string;
  purchase_checklist_id: string;
  equipment_list_id: string;
}

export interface ProjectTeamMember {
  id: number;
  email: string;
  display_name: string;
  phone: string | null;
  telegram_url: string | null;
  max_url: string | null;
  vk_url: string | null;
  role: UserRole;
  is_active: boolean;
  project_role: "owner" | "additional_instructor";
}

export interface ProjectTeamCandidate {
  id: number;
  email: string;
  display_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface ProjectTeam {
  owner: ProjectTeamMember;
  instructors: ProjectTeamMember[];
}

export async function createProject(data: CreateProjectRequest): Promise<Project> {
  return (await apiClient.post<Project>("/projects", data)).data;
}

export async function copyProject(
  projectId: number,
  data: CreateProjectRequest,
): Promise<ProjectCopyResponse> {
  return (
    await apiClient.post<ProjectCopyResponse>(`/projects/${projectId}/copy`, data)
  ).data;
}

export async function getProjects(): Promise<ProjectListResponse> {
  return (await apiClient.get<ProjectListResponse>("/projects")).data;
}

export async function getProject(projectId: number): Promise<Project> {
  return (await apiClient.get<Project>("/projects/" + projectId)).data;
}

export async function getProjectTeam(projectId: number): Promise<ProjectTeam> {
  return (await apiClient.get<ProjectTeam>(`/projects/${projectId}/team`)).data;
}

export async function getProjectTeamCandidates(
  projectId: number,
): Promise<ProjectTeamCandidate[]> {
  return (
    await apiClient.get<ProjectTeamCandidate[]>(`/projects/${projectId}/team/candidates`)
  ).data;
}

export async function updateProjectTeam(
  projectId: number,
  instructorUserIds: number[],
): Promise<ProjectTeam> {
  return (
    await apiClient.put<ProjectTeam>(`/projects/${projectId}/team`, {
      instructor_user_ids: instructorUserIds,
    })
  ).data;
}

export async function transferProjectOwnership(
  projectId: number,
  newOwnerUserId: number,
): Promise<ProjectTeam> {
  return (
    await apiClient.post<ProjectTeam>(`/projects/${projectId}/owner-transfer`, {
      new_owner_user_id: newOwnerUserId,
    })
  ).data;
}

export async function downloadProjectTeamVcard(
  projectId: number,
  userId: number,
): Promise<Blob> {
  return (
    await apiClient.get<Blob>(`/projects/${projectId}/team/${userId}/vcard`, {
      responseType: "blob",
    })
  ).data;
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

export async function completeProject(projectId: number): Promise<Project> {
  return (
    await apiClient.patch<Project>(`/projects/${projectId}/status`, {
      status: "completed",
    })
  ).data;
}

export async function deleteProject(projectId: number): Promise<void> {
  await apiClient.delete(`/projects/${projectId}`);
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
