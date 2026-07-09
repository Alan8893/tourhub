import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function MealPlanWidget() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Meal Plan</Typography>

        <Typography sx={{ mt: 1 }}>
          {preparationResult?.meal_plan_id
            ? `✓ Meal plan created: ${preparationResult.meal_plan_id}`
            : "Menu has not been generated yet."}
        </Typography>
      </CardContent>
    </Card>
  );
}
