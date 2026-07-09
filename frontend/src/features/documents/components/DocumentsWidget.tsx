import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function DocumentsWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Documents</Typography>
        <Typography>
          {projectId && preparationResult
            ? `Documents ready for project ${projectId}`
            : "Generate expedition documents."}
        </Typography>
      </CardContent>
    </Card>
  );
}
