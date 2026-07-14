import { Card, CardContent, Stack, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function ShoppingWidget() {
  const { preparationResult } = useProjectWorkflow();
  const ready = Boolean(preparationResult?.purchase_list_id);

  return (
    <Card>
      <CardContent>
        <Stack spacing={0.5}>
          <Typography variant="h6">Список закупки</Typography>
          <Typography variant="body2" color={ready ? "success.main" : "text.secondary"}>
            {ready
              ? "Список продуктов рассчитан и готов к работе."
              : "Список будет рассчитан после подготовки проекта."}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
