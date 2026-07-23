import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getProject,
  updateProjectRecipeGenerationMode,
} from "../api/projectApi";
import type { RecipeGenerationMode } from "../model/recipeGenerationMode";

export function useProject(projectId: number, enabled = true) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId),
    enabled,
  });
}

export function useUpdateProjectRecipeGenerationMode(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recipeGenerationMode: RecipeGenerationMode) =>
      updateProjectRecipeGenerationMode(projectId, recipeGenerationMode),
    onSuccess: (project) => {
      queryClient.setQueryData(["project", projectId], project);
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      void queryClient.invalidateQueries({ queryKey: ["meal-plan", projectId] });
    },
  });
}
