import { useQuery } from "@tanstack/react-query";

import { getProject } from "../api/projectApi";

export function useProject(projectId: number) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: () => getProject(projectId),
  });
}
