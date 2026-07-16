import { Button, Stack, TextField } from "@mui/material";
import { useEffect, useState } from "react";

import type { CampItem } from "../model/campItem";
import {
  isCampItemInputValid,
  normalizeCampItemName,
  parseCampItemQuantity,
} from "../model/campItemState";

interface Props {
  item: CampItem;
  readOnly: boolean;
  pending: boolean;
  onSave: (itemId: string, name: string, quantity: number) => Promise<void>;
  onRemove: (itemId: string) => Promise<void>;
}

export default function RecipeCampItemRow({
  item,
  readOnly,
  pending,
  onSave,
  onRemove,
}: Props) {
  const [name, setName] = useState(item.equipment_name);
  const [quantity, setQuantity] = useState(String(item.quantity));

  useEffect(() => {
    setName(item.equipment_name);
    setQuantity(String(item.quantity));
  }, [item]);

  const parsedQuantity = parseCampItemQuantity(quantity);
  const normalizedName = normalizeCampItemName(name);
  const changed =
    normalizedName !== item.equipment_name || parsedQuantity !== item.quantity;
  const valid = isCampItemInputValid(name, quantity);

  if (readOnly) {
    return (
      <Stack direction="row" justifyContent="space-between" spacing={2}>
        <span>{item.equipment_name}</span>
        <span>{item.quantity} шт.</span>
      </Stack>
    );
  }

  return (
    <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ sm: "center" }}>
      <TextField
        size="small"
        label="Оборудование"
        value={name}
        onChange={(event) => setName(event.target.value)}
        inputProps={{ "aria-label": `Название оборудования ${item.equipment_name}` }}
        fullWidth
      />
      <TextField
        size="small"
        label="Количество"
        value={quantity}
        onChange={(event) => setQuantity(event.target.value)}
        inputProps={{ "aria-label": `Количество оборудования ${item.equipment_name}` }}
        sx={{ width: { xs: "100%", sm: 150 } }}
      />
      <Stack direction="row" spacing={1}>
        <Button
          size="small"
          variant="outlined"
          disabled={!valid || !changed || pending || parsedQuantity === null}
          onClick={() => {
            if (parsedQuantity !== null) {
              void onSave(item.id, normalizedName, parsedQuantity);
            }
          }}
        >
          Сохранить
        </Button>
        <Button
          size="small"
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
