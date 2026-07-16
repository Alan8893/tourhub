import { Button, Chip, Stack, TextField, Typography } from "@mui/material";
import { useEffect, useState } from "react";

import type { EquipmentListItem } from "../api/equipmentListApi";
import { parseCampItemQuantity } from "../model/campItemState";

interface Props {
  item: EquipmentListItem;
  pending: boolean;
  onSave: (itemId: string, requiredQuantity: number) => Promise<void>;
  onRemove: (itemId: string) => Promise<void>;
}

export default function ProjectEquipmentItemRow({
  item,
  pending,
  onSave,
  onRemove,
}: Props) {
  const [quantity, setQuantity] = useState(String(item.required_quantity));

  useEffect(() => {
    setQuantity(String(item.required_quantity));
  }, [item.required_quantity]);

  const parsedQuantity = parseCampItemQuantity(quantity);
  const changed = parsedQuantity !== null && parsedQuantity !== item.required_quantity;
  const label = item.is_manual
    ? "Добавлено вручную"
    : item.is_overridden
      ? `Изменено · расчёт ${item.calculated_quantity}`
      : `Расчёт ${item.calculated_quantity}`;

  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      spacing={1}
      alignItems={{ sm: "center" }}
      py={1}
    >
      <Stack spacing={0.5} flex={1} minWidth={0}>
        <Typography fontWeight={600}>{item.equipment_name}</Typography>
        <Chip label={label} size="small" variant="outlined" sx={{ alignSelf: "flex-start" }} />
      </Stack>
      <TextField
        size="small"
        label="Количество"
        value={quantity}
        onChange={(event) => setQuantity(event.target.value)}
        inputProps={{
          inputMode: "numeric",
          "aria-label": `Количество: ${item.equipment_name}`,
        }}
        sx={{ width: { xs: "100%", sm: 150 } }}
      />
      <Stack direction="row" spacing={1}>
        <Button
          variant="outlined"
          disabled={pending || parsedQuantity === null || !changed}
          onClick={() => parsedQuantity !== null && void onSave(item.id, parsedQuantity)}
        >
          Сохранить
        </Button>
        <Button
          color="error"
          disabled={pending}
          onClick={() => void onRemove(item.id)}
        >
          Удалить
        </Button>
      </Stack>
    </Stack>
  );
}
