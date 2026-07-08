import { Typography } from "@mui/material";

import WorkflowModules from "./components/WorkflowModules";

export default function ProjectWorkspace() {
  return (
    <>
      <Typography variant="h4">Hiking Project Workspace</Typography>
      <Typography variant="body1" sx={{ mt: 1 }}>
        Central workspace for preparing a hiking project.
      </Typography>

      <WorkflowModules />
    </>
  );
}
