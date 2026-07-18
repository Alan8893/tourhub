import { useQuery } from "@tanstack/react-query";
import { isAxiosError } from "axios";

import { apiClient } from "@/shared/api/client";

import type { MealPlan } from "../api/mealPlanApi";

export interface MealSlotDish {
  id: string;
  dish_id: string;
  dish_name: string;
  recipe_id: string;
  recipe_name: string;
}

export interface MealSlot {
  id: string;
  day_number: number;
  meal_type: string;
  dishes: MealSlotDish[];
}

export interface ProjectMealPlan extends MealPlan {
  items: Array<{
    day_number: number;
    meal_type: string;
    dish_id: string;
    dish_name: string;
    recipe_id: string;
    recipe_name: string;
  }>;
  meals: MealSlot[];
  warnings: string[];
}

async function getProjectMealPlan(projectId: number): Promise<ProjectMealPlan | null> {
  try {
    const response = await apiClient.get<ProjectMealPlan>(
      `/meal-plans/project/${projectId}`,
    );
    return response.data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export function useProjectMealPlan(projectId: number) {
  return useQuery({
    queryKey: ["meal-plan", projectId],
    queryFn: () => getProjectMealPlan(projectId),
    enabled: projectId > 0,
    retry: (failureCount, error) => {
      if (isAxiosError(error) && error.response?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
  });
}
