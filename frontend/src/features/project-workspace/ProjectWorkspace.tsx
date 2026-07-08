import { Typography } from "@mui/material";

import { useProject } from "../project/hooks/useProject";
import ProjectHeader from "../project/components/ProjectHeader";
import WorkflowModules from "./components/WorkflowModules";

export default function ProjectWorkspace() {
  const { data: project, isLoading } = useProject(1);

  if (isLoading || !project) {
    return <Typography>Loading project...</Typography>;
  }

  return (
    <>
      <ProjectHeader project={project} />
      <Typography variant="body1" sx={{ mt: 1 }}>
        Central workspace for preparing a hiking project.
      </Typography>

      <WorkflowModules />
    </>
  );
}
