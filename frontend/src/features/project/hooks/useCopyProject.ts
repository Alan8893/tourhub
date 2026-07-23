import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  copyProject,
  type CreateProjectRequest,
  type ProjectCopyResponse,
} from "../api/projectApi";

export function useCopyProject(sourceProjectId: number) {
  const queryClient = useQueryClient();
  return useMutation<ProjectCopyResponse, Error, CreateProjectRequest>({
    mutationFn: (data) => copyProject(sourceProjectId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
