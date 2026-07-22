import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  completeProject,
  deleteProject,
  getProjectTeam,
  getProjectTeamCandidates,
  transferProjectOwnership,
  updateProjectTeam,
} from "../api/projectApi";

export function useProjectTeam(projectId: number) {
  return useQuery({
    queryKey: ["project-team", projectId],
    queryFn: () => getProjectTeam(projectId),
  });
}

export function useProjectTeamCandidates(projectId: number, enabled: boolean) {
  return useQuery({
    queryKey: ["project-team-candidates", projectId],
    queryFn: () => getProjectTeamCandidates(projectId),
    enabled,
  });
}

export function useUpdateProjectTeam(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userIds: number[]) => updateProjectTeam(projectId, userIds),
    onSuccess: (team) => {
      queryClient.setQueryData(["project-team", projectId], team);
      void queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useTransferProjectOwnership(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => transferProjectOwnership(projectId, userId),
    onSuccess: (team) => {
      queryClient.setQueryData(["project-team", projectId], team);
      void queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
      void queryClient.invalidateQueries({ queryKey: ["project-team-candidates", projectId] });
    },
  });
}

export function useCompleteProject(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => completeProject(projectId),
    onSuccess: (project) => {
      queryClient.setQueryData(["project", projectId], project);
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}

export function useDeleteProject(projectId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => deleteProject(projectId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
