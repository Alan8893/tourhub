import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/shared/api/client";

import type { MealPlan } from "../api/mealPlanApi";

export interface MealSlot {
  id: string;
  day_number: number;
  meal_type: string;
  dishes: Array<{
    day_number: number;
    meal_type: string;
    dish_id: string;
    dish_name: string;
  }>;
}

export interface ProjectMealPlan extends MealPlan {
  items: Array<{
    day_number: number;
    meal_type: string;
    dish_id: string;
    dish_name: string;
  }>;
  meals: MealSlot[];
  warnings: string[];
}

async function getProjectMealPlan(projectId: number): Promise<ProjectMealPlan> {
  const response = await apiClient.get<ProjectMealPlan>(
    `/meal-plans/project/${projectId}`,
  );

  return response.data;
}

export function useProjectMealPlan(projectId: number) {
  return useQuery({
    queryKey: ["meal-plan", projectId],
    queryFn: () => getProjectMealPlan(projectId),
  });
}
