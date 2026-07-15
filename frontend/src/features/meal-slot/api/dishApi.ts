import { apiClient } from "@/shared/api/client";

import {
  extractDishOptions,
  type DishListResponse,
  type DishOption,
} from "../model/dishOptions";

export async function getDishes(): Promise<DishOption[]> {
  const response = await apiClient.get<DishListResponse>("/dishes");
  return extractDishOptions(response.data);
}
