import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

const workflows = [
  "Meal Plan",
  "Shopping List",
  "Purchase Checklist",
  "Documents",
];

export default function ProjectWorkflowPanel() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Project Workflow</Typography>

        {workflows.map((workflow) => (
          <Typography key={workflow} sx={{ mt: 1 }}>
            {workflow === "Meal Plan"
              ? preparationResult?.meal_plan_id
                ? "✓ Meal Plan"
                : "○ Meal Plan"
              : workflow === "Shopping List"
                ? preparationResult?.purchase_list_id
                  ? "✓ Shopping List"
                  : "○ Shopping List"
                : workflow === "Purchase Checklist"
                  ? preparationResult?.purchase_checklist_id
                    ? "✓ Purchase Checklist"
                    : "○ Purchase Checklist"
                  : "○ Documents"}
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
}
