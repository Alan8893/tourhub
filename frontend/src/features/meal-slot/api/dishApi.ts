import { apiClient } from "@/shared/api/client";

export interface DishOption {
  id: string;
  name: string;
}

export async function getDishes(): Promise<DishOption[]> {
  const response = await apiClient.get<DishOption[]>("/dishes");

  return response.data;
}
