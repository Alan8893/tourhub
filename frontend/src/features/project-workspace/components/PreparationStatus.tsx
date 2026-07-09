import { Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function PreparationStatus() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Typography sx={{ mt: 2 }}>
      Project Preparation:{" "}
      {preparationResult?.meal_plan_id ? "✓ Meal Plan" : "○ Meal Plan"}{" "}
      {preparationResult?.purchase_list_id ? "✓ Shopping List" : "○ Shopping List"}{" "}
      {preparationResult?.purchase_checklist_id
        ? "✓ Purchase Checklist"
        : "○ Purchase Checklist"}{" "}
      ○ Documents
    </Typography>
  );
}
