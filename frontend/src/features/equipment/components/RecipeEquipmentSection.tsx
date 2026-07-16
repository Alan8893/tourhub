import { Alert, Button, Divider, Stack, TextField, Typography } from "@mui/material";
import { useState } from "react";

import {
  useAddCampItem,
  useRecipeCampItems,
  useRemoveCampItem,
  useUpdateCampItem,
} from "../hooks/useEquipment";
import {
  isCampItemInputValid,
  normalizeCampItemName,
  parseCampItemQuantity,
} from "../model/campItemState";
import RecipeCampItemRow from "./RecipeCampItemRow";

interface Props {
  recipeId: string;
  readOnly: boolean;
}

export default function RecipeEquipmentSection({ recipeId, readOnly }: Props) {
  const query = useRecipeCampItems(recipeId);
  const addMutation = useAddCampItem(recipeId);
  const updateMutation = useUpdateCampItem(recipeId);
  const removeMutation = useRemoveCampItem(recipeId);
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [feedback, setFeedback] = useState<string>();

  const pending =
    addMutation.isPending || updateMutation.isPending || removeMutation.isPending;
  const valid = isCampItemInputValid(name, quantity);

  async function addItem() {
    const parsedQuantity = parseCampItemQuantity(quantity);
    if (!valid || parsedQuantity === null) return;
    setFeedback(undefined);
    await addMutation.mutateAsync({
      equipment_name: normalizeCampItemName(name),
      quantity: parsedQuantity,
    });
    setName("");
    setQuantity("1");
    setFeedback("Требование добавлено.");
  }

  async function saveItem(itemId: string, nextName: string, nextQuantity: number) {
    setFeedback(undefined);
    await updateMutation.mutateAsync({
      itemId,
      input: { equipment_name: nextName, quantity: nextQuantity },
    });
    setFeedback("Требование сохранено.");
  }

  async function removeItem(itemId: string) {
    if (!window.confirm("Удалить требование оборудования?")) return;
    setFeedback(undefined);
    await removeMutation.mutateAsync(itemId);
    setFeedback("Требование удалено.");
  }

  const mutationError =
    addMutation.isError || updateMutation.isError || removeMutation.isError;

  return (
    <Stack spacing={1.5}>
      <Typography variant="h6">Оборудование для приготовления</Typography>
      <Typography variant="body2" color="text.secondary">
        Количество относится к одновременному приготовлению этого рецепта.
      </Typography>

      {query.isLoading ? <Typography>Загружаем требования...</Typography> : null}
      {query.isError ? (
        <Alert severity="error">Не удалось загрузить требования оборудования.</Alert>
      ) : null}
      {mutationError ? (
        <Alert severity="error">Не удалось сохранить требования оборудования.</Alert>
      ) : null}
      {feedback ? <Alert severity="success">{feedback}</Alert> : null}

      {!readOnly ? (
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ sm: "center" }}>
          <TextField
            size="small"
            label="Оборудование"
            value={name}
            onChange={(event) => setName(event.target.value)}
            inputProps={{ "aria-label": "Новое оборудование" }}
            fullWidth
          />
          <TextField
            size="small"
            label="Количество"
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
            inputProps={{ "aria-label": "Количество нового оборудования" }}
            sx={{ width: { xs: "100%", sm: 150 } }}
          />
          <Button
            variant="contained"
            disabled={!valid || pending}
            onClick={() => void addItem()}
          >
            Добавить
          </Button>
        </Stack>
      ) : null}

      {query.data?.items.length === 0 ? (
        <Typography color="text.secondary">Требования пока не добавлены.</Typography>
      ) : null}

      <Stack divider={<Divider flexItem />} spacing={1.5}>
        {query.data?.items.map((item) => (
          <RecipeCampItemRow
            key={item.id}
            item={item}
            readOnly={readOnly}
            pending={pending}
            onSave={saveItem}
            onRemove={removeItem}
          />
        ))}
      </Stack>
    </Stack>
  );
}
