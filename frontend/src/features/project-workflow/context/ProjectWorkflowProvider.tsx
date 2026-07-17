import { useQuery } from "@tanstack/react-query";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getProjectPreparation,
  ProjectPreparationResponse,
} from "@/features/project/api/projectApi";

interface ProjectWorkflowState {
  projectId: number;
  preparationResult?: ProjectPreparationResponse;
  setPreparationResult: (result: ProjectPreparationResponse | undefined) => void;
}

const ProjectWorkflowContext = createContext<ProjectWorkflowState | undefined>(
  undefined,
);

export function ProjectWorkflowProvider({
  projectId,
  children,
}: {
  projectId: number;
  children: ReactNode;
}) {
  const [preparationResult, setPreparationResult] = useState<
    ProjectPreparationResponse | undefined
  >();
  const preparationQuery = useQuery({
    queryKey: ["project-preparation", projectId],
    queryFn: () => getProjectPreparation(projectId),
    enabled: Number.isInteger(projectId) && projectId > 0,
    retry: false,
  });

  useEffect(() => {
    setPreparationResult(undefined);
  }, [projectId]);

  useEffect(() => {
    if (preparationQuery.data) {
      setPreparationResult(preparationQuery.data);
    }
  }, [preparationQuery.data]);

  return (
    <ProjectWorkflowContext.Provider
      value={{ projectId, preparationResult, setPreparationResult }}
    >
      {children}
    </ProjectWorkflowContext.Provider>
  );
}

export function useProjectWorkflow() {
  const context = useContext(ProjectWorkflowContext);

  if (!context) {
    throw new Error(
      "useProjectWorkflow must be used inside ProjectWorkflowProvider",
    );
  }

  return context;
}
