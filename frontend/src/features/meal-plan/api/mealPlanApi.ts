import { apiClient } from "../../../api/client";

export interface MealPlan {
  id: string;
  project_id: number | null;
  name: string;
  participants: number;
  days_count: number;
}

export async function generateProjectMealPlan(
  projectId: number,
): Promise<MealPlan> {
  const response = await apiClient.post<MealPlan>(
    `/meal-plans/project/${projectId}/generate`,
  );

  return response.data;
}
