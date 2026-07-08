import { Button, Typography } from "@mui/material";

import { useProject } from "../project/hooks/useProject";
import { usePrepareProject } from "../project/hooks/usePrepareProject";
import ProjectHeader from "../project/components/ProjectHeader";
import WorkflowModules from "./components/WorkflowModules";

export default function ProjectWorkspace() {
  const projectId = 1;
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

      <WorkflowModules />
    </>
  );
}
