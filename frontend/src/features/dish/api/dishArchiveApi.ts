import { apiClient } from "@/shared/api/client";

export interface ArchivedDish {
  id: string;
  name: string;
  recipe_name: string;
  is_archived: boolean;
  archived_by_alcohol_policy: boolean;
}

interface DishArchiveListResponse {
  items: ArchivedDish[];
}

export async function getArchivedDishes(): Promise<DishArchiveListResponse> {
  const response = await apiClient.get<DishArchiveListResponse>("/dishes/archive");
  return response.data;
}

export async function archiveDish(dishId: string): Promise<ArchivedDish> {
  const response = await apiClient.post<ArchivedDish>(`/dishes/${dishId}/archive`);
  return response.data;
}

export async function restoreDish(dishId: string): Promise<ArchivedDish> {
  const response = await apiClient.post<ArchivedDish>(`/dishes/${dishId}/restore`);
  return response.data;
}
