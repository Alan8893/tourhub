import { Button, Typography } from "@mui/material";
import { useParams } from "react-router-dom";

import { ProjectHeader, usePrepareProject, useProject } from "@/features/project";

import ProjectWorkflowPanel from "./components/ProjectWorkflowPanel";
import WorkflowModules from "./components/WorkflowModules";

export default function ProjectWorkspace() {
  const { id } = useParams();
  const projectId = Number(id ?? 1);

  const { data: project, isLoading } = useProject(projectId);
  const prepareProject = usePrepareProject();

  if (isLoading || !project) {
    return <Typography>Loading project...</Typography>;
  }

  return (
    <>
      <ProjectHeader project={project} />

      <Typography variant="body1" sx={{ mt: 1 }}>
        Central workspace for preparing a hiking project.
      </Typography>

      <Button
        variant="contained"
        sx={{ mt: 2 }}
        onClick={() => prepareProject.mutate(projectId)}
        disabled={prepareProject.isPending}
      >
        {prepareProject.isPending ? "Preparing..." : "Prepare project"}
      </Button>

      {prepareProject.isSuccess && (
        <Typography sx={{ mt: 1 }}>
          Project preparation completed.
        </Typography>
      )}

      {prepareProject.isError && (
        <Typography color="error" sx={{ mt: 1 }}>
          Project preparation failed.
        </Typography>
      )}

      <ProjectWorkflowPanel />
      <WorkflowModules />
    </>
  );
}
