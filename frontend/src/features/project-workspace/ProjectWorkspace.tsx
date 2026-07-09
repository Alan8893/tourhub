import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";

import { ProjectHeader, usePrepareProject, useProject } from "@/features/project";
import {
  ProjectWorkflowProvider,
  useProjectWorkflow,
} from "@/features/project-workflow";

import ProjectWorkflowPanel from "./components/ProjectWorkflowPanel";
import WorkflowModules from "./components/WorkflowModules";
import NextWorkflowAction from "./components/NextWorkflowAction";

function ProjectWorkspaceContent({ projectId }: { projectId: number }) {
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading || !project) {
    return <Typography>Loading project...</Typography>;
  }

  return (
    <>
      <ProjectHeader project={project} />

      <Typography variant="body1" sx={{ mt: 1 }}>
        Central workspace for preparing a hiking project.
      </Typography>

      <NextWorkflowAction />
      <ProjectWorkflowPanel />
      <WorkflowModules />
    </>
  );
}

export default function ProjectWorkspace() {
  const { id } = useParams();
  const projectId = Number(id ?? 1);

  return (
    <ProjectWorkflowProvider projectId={projectId}>
      <ProjectWorkspaceContent projectId={projectId} />
    </ProjectWorkflowProvider>
  );
}
