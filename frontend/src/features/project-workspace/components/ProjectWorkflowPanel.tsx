import {
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function ProjectWorkflowPanel() {
  const { preparationResult } = useProjectWorkflow();
  const steps = [
    {
      label: "Меню",
      detail: "Сформировано",
      complete: Boolean(preparationResult?.meal_plan_id),
    },
    {
      label: "Закупка",
      detail: "Расчёт готов",
      complete: Boolean(preparationResult?.purchase_list_id),
    },
    {
      label: "Чек-лист",
      detail: "Создан",
      complete: Boolean(preparationResult?.purchase_checklist_id),
    },
    {
      label: "Оборудование",
      detail: "Список готов",
      complete: Boolean(preparationResult?.equipment_list_id),
    },
    {
      label: "Документы",
      detail: "Готовы к скачиванию",
      complete: Boolean(
        preparationResult?.purchase_list_id &&
          preparationResult.purchase_checklist_id &&
          preparationResult.equipment_list_id,
      ),
    },
  ];
  const completed = steps.filter((step) => step.complete).length;

  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Готовность проекта</Typography>
            <Typography variant="h4" component="p" fontWeight={700}>
              {completed} из {steps.length}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(completed / steps.length) * 100}
              aria-label="Готовность проекта"
              sx={{ height: 7, borderRadius: 999 }}
            />
          </Stack>

          <Stack spacing={1.25}>
            {steps.map((step) => (
              <Stack
                key={step.label}
                direction="row"
                spacing={1}
                alignItems="center"
                justifyContent="space-between"
              >
                <Typography>
                  <Typography
                    component="span"
                    color={step.complete ? "success.main" : "text.disabled"}
                    aria-hidden
                  >
                    {step.complete ? "✓" : "○"}
                  </Typography>{" "}
                  {step.label}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {step.complete ? step.detail : "Не готово"}
                </Typography>
              </Stack>
            ))}
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}
