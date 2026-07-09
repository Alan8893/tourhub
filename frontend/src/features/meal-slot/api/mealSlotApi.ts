import { apiClient } from "@/shared/api/client";

export interface MealSlotDishMutationResult {
  id: string;
  dish_id: string;
}

export async function addMealSlotDish(
  slotId: string,
  dishId: string,
): Promise<MealSlotDishMutationResult> {
  const response = await apiClient.post<MealSlotDishMutationResult>(
    `/meal-slots/${slotId}/dishes/${dishId}`,
  );

  return response.data;
}

export async function removeMealSlotDish(
  slotId: string,
  slotDishId: string,
): Promise<void> {
  await apiClient.delete(
    `/meal-slots/${slotId}/dishes/${slotDishId}`,
  );
}

export async function replaceMealSlotDish(
  slotId: string,
  slotDishId: string,
  dishId: string,
): Promise<MealSlotDishMutationResult> {
  const response = await apiClient.put<MealSlotDishMutationResult>(
    `/meal-slots/${slotId}/dishes/${slotDishId}/${dishId}`,
  );

  return response.data;
}
