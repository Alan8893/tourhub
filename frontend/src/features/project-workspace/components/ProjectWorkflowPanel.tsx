import { Card, CardContent, Typography } from "@mui/material";

const workflows = [
  "Meal Plan",
  "Shopping List",
  "Purchase Checklist",
  "Documents",
];

export default function ProjectWorkflowPanel() {
  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Project Workflow</Typography>

        {workflows.map((workflow) => (
          <Typography key={workflow} sx={{ mt: 1 }}>
            {workflow}
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
}
