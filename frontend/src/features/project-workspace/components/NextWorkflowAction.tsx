import { Button, Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";
import { useGenerateMealPlan } from "@/features/meal-plan/hooks/useGenerateMealPlan";
import { usePrepareProject } from "@/features/project";

export default function NextWorkflowAction() {
  const { projectId, preparationResult, setPreparationResult } = useProjectWorkflow();
  const generateMealPlan = useGenerateMealPlan();
  const prepareProject = usePrepareProject();

  if (!preparationResult?.meal_plan_id) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6">Next Action</Typography>
          <Typography sx={{ mb: 1 }}>
            Generate meal plan for this project.
          </Typography>
          <Button
            variant="contained"
            onClick={() =>
              generateMealPlan.mutate(projectId, {
                onSuccess: (result) =>
                  setPreparationResult({
                    project_id: projectId,
                    meal_plan_id: result.id,
                    purchase_list_id: "",
                    purchase_checklist_id: "",
                  }),
              })
            }
            disabled={generateMealPlan.isPending}
          >
            {generateMealPlan.isPending ? "Generating..." : "Generate Meal Plan"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (
    !preparationResult.purchase_list_id ||
    !preparationResult.purchase_checklist_id
  ) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6">Next Action</Typography>
          <Typography sx={{ mb: 1 }}>
            Prepare shopping list and checklist.
          </Typography>
          <Button
            variant="contained"
            onClick={() =>
              prepareProject.mutate(projectId, {
                onSuccess: (result) => setPreparationResult(result),
              })
            }
            disabled={prepareProject.isPending}
          >
            {prepareProject.isPending ? "Preparing..." : "Prepare Project"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Next Action</Typography>
        <Typography>
          Project preparation completed. Documents are ready for export.
        </Typography>
      </CardContent>
    </Card>
  );
}
