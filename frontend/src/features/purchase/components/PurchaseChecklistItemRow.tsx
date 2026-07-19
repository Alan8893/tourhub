import {
  Alert,
  Button,
  Checkbox,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useState } from "react";

import { PurchaseChecklistItem } from "../api/purchaseChecklistApi";
import { useUpdatePurchaseChecklistItem } from "../hooks/usePurchaseChecklist";
import {
  formatPurchaseQuantity,
  parsePurchasedQuantity,
  purchaseChecklistResponsiveDirection,
} from "../model/purchaseChecklistState";

interface PurchaseChecklistItemRowProps {
  item: PurchaseChecklistItem;
  projectId: number;
}

export default function PurchaseChecklistItemRow({
  item,
  projectId,
}: PurchaseChecklistItemRowProps) {
  const updateItem = useUpdatePurchaseChecklistItem(projectId);
  const [purchasedValue, setPurchasedValue] = useState(
    formatPurchaseQuantity(item.purchased_quantity),
  );
  const [feedback, setFeedback] = useState<
    { severity: "success" | "error"; message: string } | undefined
  >();

  useEffect(() => {
    setPurchasedValue(formatPurchaseQuantity(item.purchased_quantity));
  }, [item.id, item.purchased_quantity]);

  const savePurchasedQuantity = () => {
    const purchasedQuantity = parsePurchasedQuantity(purchasedValue);
    if (purchasedQuantity === null) {
      setFeedback({
        severity: "error",
        message: "Введите неотрицательное количество.",
      });
      return;
    }

    setFeedback(undefined);
    updateItem.mutate(
      {
        itemId: item.id,
        input: { purchased_quantity: purchasedQuantity },
      },
      {
        onSuccess: () => {
          setFeedback({ severity: "success", message: "Количество сохранено." });
        },
        onError: () => {
          setFeedback({
            severity: "error",
            message: "Не удалось сохранить количество.",
          });
        },
      },
    );
  };

  const setChecked = (checked: boolean) => {
    setFeedback(undefined);
    updateItem.mutate(
      {
        itemId: item.id,
        input: { is_checked: checked },
      },
      {
        onSuccess: () => {
          setFeedback({
            severity: "success",
            message: checked ? "Позиция отмечена купленной." : "Отметка снята.",
          });
        },
        onError: () => {
          setFeedback({
            severity: "error",
            message: "Не удалось изменить отметку.",
          });
        },
      },
    );
  };

  return (
    <Stack spacing={1.25} sx={{ py: 1.5 }}>
      <Stack
        direction={purchaseChecklistResponsiveDirection}
        spacing={1.5}
        alignItems={{ xs: "stretch", md: "center" }}
      >
        <Stack spacing={0.25} sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="subtitle1" fontWeight={600}>
            {item.product_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Требуется: {formatPurchaseQuantity(item.required_quantity)} {item.unit}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Осталось: {formatPurchaseQuantity(item.remaining_quantity)} {item.unit}
          </Typography>
        </Stack>

        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1}
          alignItems={{ xs: "stretch", sm: "center" }}
          sx={{ width: { xs: "100%", md: "auto" } }}
        >
          <TextField
            size="small"
            type="number"
            label="Куплено"
            value={purchasedValue}
            onChange={(event) => setPurchasedValue(event.target.value)}
            inputProps={{
              min: 0,
              step: "any",
              "aria-label": `Куплено для ${item.product_name}`,
            }}
            sx={{ width: { xs: "100%", sm: 170 } }}
          />

          <Button
            variant="outlined"
            onClick={savePurchasedQuantity}
            disabled={updateItem.isPending}
          >
            Сохранить
          </Button>

          <FormControlLabel
            sx={{ m: 0, whiteSpace: "nowrap" }}
            control={
              <Checkbox
                checked={item.is_checked}
                onChange={(event) => setChecked(event.target.checked)}
                disabled={updateItem.isPending}
                inputProps={{
                  "aria-label": `Отметить ${item.product_name} купленным`,
                }}
              />
            }
            label="Куплено"
          />
        </Stack>
      </Stack>

      {feedback ? (
        <Alert severity={feedback.severity} role="alert">
          {feedback.message}
        </Alert>
      ) : null}
    </Stack>
  );
}
