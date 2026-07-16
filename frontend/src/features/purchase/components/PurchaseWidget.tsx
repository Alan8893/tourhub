import {
  Alert,
  Card,
  CardContent,
  Divider,
  LinearProgress,
  Stack,
  Typography,
} from "@mui/material";
import { Fragment } from "react";

import { useProjectWorkflow } from "@/features/project-workflow";

import { useProjectPurchaseChecklist } from "../hooks/usePurchaseChecklist";
import { getChecklistProgress } from "../model/purchaseChecklistState";
import PurchaseChecklistItemRow from "./PurchaseChecklistItemRow";

export default function PurchaseWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const checklistQuery = useProjectPurchaseChecklist(
    projectId,
    preparationResult?.purchase_checklist_id,
  );
  const checklist = checklistQuery.data;
  const progress = checklist ? getChecklistProgress(checklist.items) : undefined;
  const progressPercent = progress?.total
    ? (progress.checked / progress.total) * 100
    : 0;

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Чек-лист покупок</Typography>

          {checklistQuery.isLoading ? (
            <Typography color="text.secondary">Загружаем позиции...</Typography>
          ) : null}

          {checklistQuery.isError ? (
            <Alert severity="error" role="alert">
              Не удалось загрузить чек-лист покупок.
            </Alert>
          ) : null}

          {!checklistQuery.isLoading && !checklistQuery.isError && !checklist ? (
            <Typography variant="body2" color="text.secondary">
              Чек-лист появится после подготовки проекта.
            </Typography>
          ) : null}

          {checklist && progress ? (
            <>
              <Stack spacing={0.5}>
                <Typography variant="body2" color="text.secondary">
                  Отмечено {progress.checked} из {progress.total}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progressPercent}
                  aria-label="Прогресс закупок"
                />
              </Stack>

              <Stack divider={<Divider flexItem />}>
                {checklist.items.map((item) => (
                  <Fragment key={item.id}>
                    <PurchaseChecklistItemRow item={item} projectId={projectId} />
                  </Fragment>
                ))}
              </Stack>
            </>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
