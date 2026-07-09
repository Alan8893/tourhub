import { useMutation, useQueryClient } from "@tanstack/react-query";

import { generateProjectMealPlan } from "../api/mealPlanApi";

export function useGenerateMealPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: generateProjectMealPlan,
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({
        queryKey: ["project", projectId],
      });
    },
  });
}
