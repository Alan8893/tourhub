import { apiClient } from "@/shared/api/client";
import type { CampItem } from "../model/campItem";

export async function updateCampItem(
  recipeId: string,
  itemId: string,
  input: Omit<CampItem, "id">,
) {
  const path = "/recipes/" + recipeId + "/equipment" + "-requirements/" + itemId;
  return (await apiClient.put<CampItem>(path, input)).data;
}
