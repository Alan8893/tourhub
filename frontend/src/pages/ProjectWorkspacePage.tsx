import { Box, Stack } from "@mui/material";
import { useState } from "react";
import { useLocation } from "react-router-dom";

import type { ProjectCopyResponse } from "../features/project/api/projectApi";
import ProjectCopyResultNotice from "../features/project/components/ProjectCopyResultNotice";
import ProjectWorkspace from "../features/project-workspace/ProjectWorkspace";

interface ProjectWorkspaceLocationState {
  projectCopyResult?: ProjectCopyResponse;
}

export default function ProjectWorkspacePage() {
  const location = useLocation();
  const navigationState = location.state as ProjectWorkspaceLocationState | null;
  const [copyResult, setCopyResult] = useState<ProjectCopyResponse | null>(
    navigationState?.projectCopyResult ?? null,
  );

  return (
    <Box sx={{ pb: 4 }}>
      <Stack spacing={2}>
        {copyResult && (
          <ProjectCopyResultNotice
            result={copyResult}
            onClose={() => setCopyResult(null)}
          />
        )}
        <ProjectWorkspace />
      </Stack>
    </Box>
  );
}
