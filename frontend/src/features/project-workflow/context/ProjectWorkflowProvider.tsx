import { createContext, ReactNode, useContext, useState } from "react";

interface ProjectWorkflowState {
  projectId: number;
  preparationResult?: {
    project_id: number;
    meal_plan_id: string;
    purchase_list_id: string;
    purchase_checklist_id: string;
  };
  setPreparationResult: (result: ProjectWorkflowState["preparationResult"]) => void;
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
    ProjectWorkflowState["preparationResult"]
  >();

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
