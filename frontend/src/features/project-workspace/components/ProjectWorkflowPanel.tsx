import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function ProjectWorkflowPanel() {
  const { preparationResult } = useProjectWorkflow();
  const steps = [
    {
      label: "Меню похода",
      complete: Boolean(preparationResult?.meal_plan_id),
    },
    {
      label: "Закупка продуктов",
      complete: Boolean(preparationResult?.purchase_list_id),
    },
    {
      label: "Чек-лист покупок",
      complete: Boolean(preparationResult?.purchase_checklist_id),
    },
    {
      label: "Оборудование",
      complete: Boolean(preparationResult?.equipment_list_id),
    },
    {
      label: "Документы",
      complete: Boolean(
        preparationResult?.purchase_list_id &&
          preparationResult.purchase_checklist_id &&
          preparationResult.equipment_list_id,
      ),
      completeLabel: "Документы готовы",
    },
  ];

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Подготовка проекта</Typography>

        {steps.map((step) => (
          <Typography key={step.label} sx={{ mt: 1 }}>
            {step.complete ? "✓" : "○"} {step.complete ? step.completeLabel ?? step.label : step.label}
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
}
