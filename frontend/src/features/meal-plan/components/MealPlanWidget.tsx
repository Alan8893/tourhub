import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function MealPlanWidget() {
  const { preparationResult } = useProjectWorkflow();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Meal Plan</Typography>
        <Typography>
          {preparationResult?.meal_plan_id
            ? `Meal plan: ${preparationResult.meal_plan_id}`
            : "Manage hike nutrition planning."}
        </Typography>
      </CardContent>
    </Card>
  );
}
