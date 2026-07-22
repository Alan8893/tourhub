import { Alert, Button, Card, CardContent, Stack, Typography } from "@mui/material";

import { useProjectMealPlan } from "@/features/meal-plan";
import { useGenerateMealPlan } from "@/features/meal-plan/hooks/useGenerateMealPlan";
import { usePrepareProject } from "@/features/project";
import { useProjectWorkflow } from "@/features/project-workflow";

interface Props {
  canEditMenu: boolean;
  canManageProject: boolean;
  completed: boolean;
}

export default function NextWorkflowAction({
  canEditMenu,
  canManageProject,
  completed,
}: Props) {
  const { projectId, preparationResult, setPreparationResult } = useProjectWorkflow();
  const { data: mealPlan, isLoading: isMealPlanLoading } = useProjectMealPlan(projectId);
  const generateMealPlan = useGenerateMealPlan();
  const prepareProject = usePrepareProject();

  const hasMealPlan = Boolean(mealPlan ?? preparationResult?.meal_plan_id);

  if (completed) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h6">Проект завершён</Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Проект сохранён как история похода и доступен только для чтения.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (isMealPlanLoading && !preparationResult?.meal_plan_id) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Typography>Проверяем состояние проекта…</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!hasMealPlan) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Stack spacing={1.25} alignItems="flex-start">
            <Typography variant="h6">Следующее действие</Typography>
            <Typography>
              {canEditMenu
                ? "Сформируйте меню для этого похода."
                : "Владелец проекта ещё не сформировал меню."}
            </Typography>
            {canEditMenu && generateMealPlan.isError && (
              <Alert severity="error">
                Не удалось сформировать меню. Проверьте данные проекта и повторите попытку.
              </Alert>
            )}
            {canEditMenu && (
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
                        equipment_list_id: "",
                      }),
                  })
                }
                disabled={generateMealPlan.isPending}
              >
                {generateMealPlan.isPending ? "Формирование…" : "Сформировать меню"}
              </Button>
            )}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  if (
    !preparationResult?.purchase_list_id ||
    !preparationResult.purchase_checklist_id ||
    !preparationResult.equipment_list_id
  ) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Stack spacing={1.25} alignItems="flex-start">
            <Typography variant="h6">Следующее действие</Typography>
            <Typography>
              {canManageProject
                ? "Рассчитайте закупку, создайте чек-лист и список оборудования."
                : "Владелец проекта ещё не выполнил полную подготовку."}
            </Typography>
            {canManageProject && prepareProject.isError && (
              <Alert severity="error">
                Не удалось подготовить проект. Проверьте состав меню и повторите попытку.
              </Alert>
            )}
            {canManageProject && (
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
            )}
          </Stack>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6">Проект подготовлен</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.5 }}>
          Закупка, чек-лист и оборудование сформированы. Документы доступны для скачивания.
        </Typography>
      </CardContent>
    </Card>
  );
}
