import { Alert, AlertTitle, Box, Typography } from "@mui/material";

import type { ProjectCopyResponse } from "../api/projectApi";
import { projectCopySummary } from "../model/projectCopy";

interface Props {
  result: ProjectCopyResponse;
  onClose?: () => void;
}

export default function ProjectCopyResultNotice({ result, onClose }: Props) {
  const warnings = result.warnings.slice(0, 20);

  return (
    <Alert severity={warnings.length ? "warning" : "success"} onClose={onClose}>
      <AlertTitle>Проект скопирован</AlertTitle>
      <Typography variant="body2">{projectCopySummary(result)}</Typography>
      {warnings.length > 0 && (
        <Box component="ul" sx={{ pl: 2.5, mb: 0, mt: 1 }}>
          {warnings.map((warning, index) => (
            <li key={`${index}-${warning}`}>
              <Typography variant="body2">{warning}</Typography>
            </li>
          ))}
        </Box>
      )}
    </Alert>
  );
}
