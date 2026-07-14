import { apiClient } from "@/shared/api/client";

export interface DishRecipe {
  id: string;
  name: string;
  is_archived: boolean;
}

export interface Dish {
  id: string;
  name: string;
  recipe: DishRecipe;
}

export interface DishListResponse {
  items: Dish[];
}

export interface DishWriteInput {
  name: string;
  recipe_id: string;
}

export async function getDishes(): Promise<DishListResponse> {
  const response = await apiClient.get<DishListResponse>("/dishes");
  return response.data;
}

export async function getDish(dishId: string): Promise<Dish> {
  const response = await apiClient.get<Dish>(`/dishes/${dishId}`);
  return response.data;
}

export async function createDish(input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.post<Dish>("/dishes", input);
  return response.data;
}

export async function updateDish(dishId: string, input: DishWriteInput): Promise<Dish> {
  const response = await apiClient.put<Dish>(`/dishes/${dishId}`, input);
  return response.data;
}
