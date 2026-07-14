import { Card, CardContent, Stack, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

export default function PurchaseWidget() {
  const { preparationResult } = useProjectWorkflow();
  const ready = Boolean(preparationResult?.purchase_checklist_id);

  return (
    <Card>
      <CardContent>
        <Stack spacing={0.5}>
          <Typography variant="h6">Чек-лист покупок</Typography>
          <Typography variant="body2" color={ready ? "success.main" : "text.secondary"}>
            {ready
              ? "Чек-лист создан. Можно отмечать купленные продукты."
              : "Чек-лист появится после подготовки проекта."}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
