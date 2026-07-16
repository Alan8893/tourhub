import {
  Alert,
  Card,
  CardContent,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

import { useProjectPurchaseList } from "../hooks/usePurchaseList";
import { getPurchaseListSummary } from "../model/purchaseListState";
import PurchaseListItemRow from "./PurchaseListItemRow";

export default function ShoppingWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const purchaseListQuery = useProjectPurchaseList(
    projectId,
    preparationResult?.purchase_list_id,
  );
  const purchaseList = purchaseListQuery.data;
  const summary = purchaseList
    ? getPurchaseListSummary(purchaseList.items)
    : undefined;

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Фасовка и объём закупки</Typography>

          {purchaseListQuery.isLoading ? (
            <Typography color="text.secondary">Загружаем расчёт упаковок...</Typography>
          ) : null}

          {purchaseListQuery.isError ? (
            <Alert severity="error" role="alert">
              Не удалось загрузить список закупки.
            </Alert>
          ) : null}

          {!purchaseListQuery.isLoading &&
          !purchaseListQuery.isError &&
          !purchaseList ? (
            <Typography variant="body2" color="text.secondary">
              Расчёт упаковок появится после подготовки проекта.
            </Typography>
          ) : null}

          {purchaseList && summary ? (
            <>
              <Typography variant="body2" color="text.secondary">
                Позиций: {summary.itemsTotal} · Упаковок: {summary.packagesTotal} · С
                излишком: {summary.surplusItems}
              </Typography>

              <Stack divider={<Divider flexItem />}>
                {purchaseList.items.map((item) => (
                  <PurchaseListItemRow key={item.id} item={item} />
                ))}
              </Stack>
            </>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
