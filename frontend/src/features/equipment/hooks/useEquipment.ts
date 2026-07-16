import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getProjectEquipmentList } from "../api/equipmentListApi";
import { addCampItem, getCampItems } from "../api/recipeCampItemApi";
import { removeCampItem } from "../api/removeCampItem";
import { updateCampItem } from "../api/updateCampItem";
import type { CampItem } from "../model/campItem";

export function useRecipeCampItems(recipeId: string) {
  return useQuery({
    queryKey: ["recipe-camp-items", recipeId],
    queryFn: () => getCampItems(recipeId),
    enabled: recipeId.length > 0,
  });
}

function useInvalidateCampItems(recipeId: string) {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["recipe-camp-items", recipeId] });
}

export function useAddCampItem(recipeId: string) {
  const invalidate = useInvalidateCampItems(recipeId);
  return useMutation({
    mutationFn: (input: Omit<CampItem, "id">) => addCampItem(recipeId, input),
    onSuccess: invalidate,
  });
}

export function useUpdateCampItem(recipeId: string) {
  const invalidate = useInvalidateCampItems(recipeId);
  return useMutation({
    mutationFn: ({ itemId, input }: { itemId: string; input: Omit<CampItem, "id"> }) =>
      updateCampItem(recipeId, itemId, input),
    onSuccess: invalidate,
  });
}

export function useRemoveCampItem(recipeId: string) {
  const invalidate = useInvalidateCampItems(recipeId);
  return useMutation({
    mutationFn: (itemId: string) => removeCampItem(recipeId, itemId),
    onSuccess: invalidate,
  });
}

export function useProjectEquipmentList(projectId: number, refreshKey?: string) {
  return useQuery({
    queryKey: ["project-equipment", projectId, refreshKey ?? "stored"],
    queryFn: () => getProjectEquipmentList(projectId),
    enabled: Number.isInteger(projectId) && projectId > 0,
    retry: false,
  });
}
