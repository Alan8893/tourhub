import { useMutation } from "@tanstack/react-query";

import { createProject, CreateProjectRequest } from "../api/projectApi";

export function useCreateProject() {
  return useMutation({
    mutationFn: (data: CreateProjectRequest) => createProject(data),
  });
}
