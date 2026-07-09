import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useProjectWorkflow } from "@/features/project-workflow";

import { prepareProject } from "../api/projectApi";

export function usePrepareProject() {
  const queryClient = useQueryClient();
  const { setPreparationResult } = useProjectWorkflow();

  return useMutation({
    mutationFn: prepareProject,
    onSuccess: (data, projectId) => {
      setPreparationResult(data);

      queryClient.invalidateQueries({
        queryKey: ["project", projectId],
      });
    },
  });
}
