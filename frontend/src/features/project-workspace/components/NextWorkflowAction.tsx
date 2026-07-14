import { Alert, Button, Card, CardContent, Stack, Typography } from "@mui/material";

import { useGenerateMealPlan } from "@/features/meal-plan/hooks/useGenerateMealPlan";
import { usePrepareProject } from "@/features/project";
import { useProjectWorkflow } from "@/features/project-workflow";

export default function NextWorkflowAction() {
  const { projectId, preparationResult, setPreparationResult } = useProjectWorkflow();
  const generateMealPlan = useGenerateMealPlan();
  const prepareProject = usePrepareProject();

  if (!preparationResult?.meal_plan_id) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">Следующее действие</Typography>
            <Typography>Сформируйте меню для этого похода.</Typography>
            {(generateMealPlan.isError) && (
              <Alert severity="error">Не удалось сформировать меню. Проверьте данные проекта и повторите попытку.</Alert>
            )}
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
              {generateMealPlan.isPending ? "Формирование…" : "Сформировать меню"}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  if (!preparationResult.purchase_list_id || !preparationResult.purchase_checklist_id) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Stack spacing={1}>
            <Typography variant="h6">Следующее действие</Typography>
            <Typography>Рассчитайте закупку и создайте чек-лист.</Typography>
            {prepareProject.isError && (
              <Alert severity="error">Не удалось подготовить закупку. Проверьте состав меню и повторите попытку.</Alert>
            )}
            <Button
              variant="contained"
              onClick={() =>
                prepareProject.mutate(projectId, {
                  onSuccess: (result) => setPreparationResult(result),
                })
              }
              disabled={prepareProject.isPending}
            >
              {prepareProject.isPending ? "Подготовка…" : "Подготовить проект"}
            </Button>
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Проект подготовлен</Typography>
        <Typography>Закупка и чек-лист сформированы. Документы доступны для скачивания.</Typography>
      </CardContent>
    </Card>
  );
}
