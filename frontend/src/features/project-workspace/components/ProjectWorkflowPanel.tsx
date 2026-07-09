import { Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

const workflows = [
  "Меню похода",
  "Закупка продуктов",
  "Чек-лист покупок",
  "Документы",
];

export default function ProjectWorkflowPanel() {
  const { preparationResult } = useProjectWorkflow();

  const documentsReady = Boolean(
    preparationResult?.purchase_list_id &&
      preparationResult?.purchase_checklist_id,
  );

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6">Подготовка проекта</Typography>

        {workflows.map((workflow) => (
          <Typography key={workflow} sx={{ mt: 1 }}>
            {workflow === "Меню похода"
              ? preparationResult?.meal_plan_id
                ? "✓ Меню похода"
                : "○ Меню похода"
              : workflow === "Закупка продуктов"
                ? preparationResult?.purchase_list_id
                  ? "✓ Закупка продуктов"
                  : "○ Закупка продуктов"
                : workflow === "Чек-лист покупок"
                  ? preparationResult?.purchase_checklist_id
                    ? "✓ Чек-лист покупок"
                    : "○ Чек-лист покупок"
                  : documentsReady
                    ? "✓ Документы готовы"
                    : "○ Документы"}
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
}
