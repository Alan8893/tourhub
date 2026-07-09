import { Button, Card, CardContent, Typography } from "@mui/material";
import { useProjectWorkflow } from "@/features/project-workflow";
import { useGenerateMealPlan } from "../hooks/useGenerateMealPlan";

export default function MealPlanWidget() {
  const { projectId, setPreparationResult } = useProjectWorkflow();
  const generateMealPlan = useGenerateMealPlan();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Meal Plan</Typography>

        <Button
          variant="contained"
          sx={{ mt: 1 }}
          onClick={() =>
            generateMealPlan.mutate(projectId, {
              onSuccess: (result) => {
                setPreparationResult({
                  project_id: projectId,
                  meal_plan_id: result.id,
                  purchase_list_id: "",
                  purchase_checklist_id: "",
                });
              },
            })
          }
          disabled={generateMealPlan.isPending}
        >
          {generateMealPlan.isPending ? "Generating..." : "Generate Meal Plan"}
        </Button>

        <Typography sx={{ mt: 1 }}>
          {generateMealPlan.isSuccess
            ? `Meal plan: ${generateMealPlan.data.id}`
            : "Manage hike nutrition planning."}
        </Typography>
      </CardContent>
    </Card>
  );
}
