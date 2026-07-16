import { createContext, ReactNode, useContext, useState } from "react";

interface ProjectPreparationResult {
  project_id: number;
  meal_plan_id: string;
  purchase_list_id: string;
  purchase_checklist_id: string;
  equipment_list_id: string;
}

interface ProjectWorkflowState {
  projectId: number;
  preparationResult?: ProjectPreparationResult;
  setPreparationResult: (result: ProjectPreparationResult | undefined) => void;
}

const ProjectWorkflowContext = createContext<ProjectWorkflowState | undefined>(
  undefined,
);

export function ProjectWorkflowProvider({
  projectId,
  children,
  initialPreparationResult,
}: {
  projectId: number;
  children: ReactNode;
  initialPreparationResult?: ProjectPreparationResult;
}) {
  const [preparationResult, setPreparationResult] = useState<
    ProjectPreparationResult | undefined
  >(initialPreparationResult);

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
