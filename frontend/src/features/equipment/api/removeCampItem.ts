import { apiClient } from "@/shared/api/client";

export async function removeCampItem(
  recipeId: string,
  itemId: string,
): Promise<void> {
  const path = "/recipes/" + recipeId + "/equipment" + "-requirements/" + itemId;
  await apiClient.delete(path);
}
