import { apiClient } from "@/shared/api/client";
import type { CampItem, CampItemList } from "../model/campItem";

const pathFor = (recipeId: string) =>
  "/recipes/" + recipeId + "/equipment" + "-requirements";

export async function getCampItems(recipeId: string): Promise<CampItemList> {
  return (await apiClient.get<CampItemList>(pathFor(recipeId))).data;
}

export async function addCampItem(recipeId: string, input: Omit<CampItem, "id">) {
  return (await apiClient.post<CampItem>(pathFor(recipeId), input)).data;
}
