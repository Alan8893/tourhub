import { Alert, Card, CardContent, Divider, Stack, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

import { useProjectEquipmentList } from "../hooks/useEquipment";
import { getEquipmentSummary } from "../model/campItemState";

export default function CampInventoryWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const query = useProjectEquipmentList(projectId, preparationResult?.equipment_list_id);
  const list = query.data;
  const summary = list ? getEquipmentSummary(list.items) : undefined;

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Оборудование</Typography>
          <Typography variant="body2" color="text.secondary">
            Максимальная одновременная потребность по всему меню.
          </Typography>
          {query.isLoading ? <Typography>Загружаем список...</Typography> : null}
          {query.isError ? <Alert severity="error">Не удалось загрузить список.</Alert> : null}
          {!query.isLoading && !query.isError && !list ? (
            <Typography color="text.secondary">Список появится после подготовки проекта.</Typography>
          ) : null}
          {list && summary ? (
            <>
              <Typography variant="body2" color="text.secondary">
                Позиций: {summary.positions} · Всего единиц: {summary.totalUnits}
              </Typography>
              {list.items.length === 0 ? (
                <Typography color="text.secondary">В рецептах нет требований.</Typography>
              ) : (
                <Stack divider={<Divider flexItem />}>
                  {list.items.map((item) => (
                    <Stack key={item.id} direction="row" justifyContent="space-between" spacing={2} py={1}>
                      <Typography>{item.equipment_name}</Typography>
                      <Typography fontWeight={600} whiteSpace="nowrap">{item.required_quantity} шт.</Typography>
                    </Stack>
                  ))}
                </Stack>
              )}
            </>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
