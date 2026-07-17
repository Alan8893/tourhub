import { Typography } from "@mui/material";
import { useParams } from "react-router-dom";

import { ProjectHeader, useProject } from "@/features/project";
import {
  ProjectWorkflowProvider,
} from "@/features/project-workflow";

import NextWorkflowAction from "./components/NextWorkflowAction";
import ProjectWorkflowPanel from "./components/ProjectWorkflowPanel";
import WorkflowModules from "./components/WorkflowModules";

function ProjectWorkspaceContent({ projectId }: { projectId: number }) {
  const { data: project, isLoading } = useProject(projectId);

  if (isLoading || !project) {
    return <Typography>Загружаем проект…</Typography>;
  }

  return (
    <>
      <ProjectHeader project={project} />

      <Typography variant="body1" sx={{ mt: 1 }}>
        Единое рабочее пространство для подготовки похода.
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
