import { useMutation, useQueryClient } from "@tanstack/react-query";

import { prepareProject } from "../api/projectApi";

export function usePrepareProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: prepareProject,
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({
        queryKey: ["project", projectId],
      });
    },
  });
}
