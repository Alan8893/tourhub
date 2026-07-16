import {
  Alert,
  Button,
  Card,
  CardContent,
  Divider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useState } from "react";

import { useProjectWorkflow } from "@/features/project-workflow";

import {
  useAddProjectEquipmentItem,
  useProjectEquipmentList,
  useRemoveProjectEquipmentItem,
  useUpdateProjectEquipmentItem,
} from "../hooks/useEquipment";
import {
  getEquipmentSummary,
  isCampItemInputValid,
  normalizeCampItemName,
  parseCampItemQuantity,
} from "../model/campItemState";
import ProjectEquipmentItemRow from "./ProjectEquipmentItemRow";

export default function CampInventoryWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const query = useProjectEquipmentList(projectId, preparationResult?.equipment_list_id);
  const addMutation = useAddProjectEquipmentItem(projectId);
  const updateMutation = useUpdateProjectEquipmentItem(projectId);
  const removeMutation = useRemoveProjectEquipmentItem(projectId);
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [feedback, setFeedback] = useState<string>();
  const list = query.data;
  const summary = list ? getEquipmentSummary(list.items) : undefined;
  const pending =
    addMutation.isPending || updateMutation.isPending || removeMutation.isPending;
  const valid = isCampItemInputValid(name, quantity);

  async function addItem() {
    const parsedQuantity = parseCampItemQuantity(quantity);
    if (!valid || parsedQuantity === null) return;
    setFeedback(undefined);
    await addMutation.mutateAsync({
      equipment_name: normalizeCampItemName(name),
      required_quantity: parsedQuantity,
    });
    setName("");
    setQuantity("1");
    setFeedback("Позиция добавлена вручную.");
  }

  async function saveItem(itemId: string, requiredQuantity: number) {
    setFeedback(undefined);
    await updateMutation.mutateAsync({ itemId, requiredQuantity });
    setFeedback("Количество сохранено.");
  }

  async function removeItem(itemId: string) {
    if (!window.confirm("Удалить позицию из списка оборудования?")) return;
    setFeedback(undefined);
    await removeMutation.mutateAsync(itemId);
    setFeedback("Позиция удалена. Изменение сохранится при пересчёте.");
  }

  const mutationError =
    addMutation.isError || updateMutation.isError || removeMutation.isError;

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Оборудование</Typography>
          <Typography variant="body2" color="text.secondary">
            Максимальная одновременная потребность по меню. Итоговый список можно изменить вручную.
          </Typography>
          {query.isLoading ? <Typography>Загружаем список...</Typography> : null}
          {query.isError ? <Alert severity="error">Не удалось загрузить список.</Alert> : null}
          {mutationError ? (
            <Alert severity="error">Не удалось сохранить изменение оборудования.</Alert>
          ) : null}
          {feedback ? <Alert severity="success">{feedback}</Alert> : null}
          {!query.isLoading && !query.isError && !list ? (
            <Typography color="text.secondary">Список появится после подготовки проекта.</Typography>
          ) : null}
          {list && summary ? (
            <>
              <Typography variant="body2" color="text.secondary">
                Позиций: {summary.positions} · Всего единиц: {summary.totalUnits}
              </Typography>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={1}
                alignItems={{ sm: "center" }}
              >
                <TextField
                  size="small"
                  label="Новое оборудование"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  inputProps={{ "aria-label": "Новое оборудование проекта" }}
                  fullWidth
                />
                <TextField
                  size="small"
                  label="Количество"
                  value={quantity}
                  onChange={(event) => setQuantity(event.target.value)}
                  inputProps={{
                    inputMode: "numeric",
                    "aria-label": "Количество нового оборудования проекта",
                  }}
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
              {list.items.length === 0 ? (
                <Typography color="text.secondary">В списке пока нет позиций.</Typography>
              ) : (
                <Stack divider={<Divider flexItem />}>
                  {list.items.map((item) => (
                    <ProjectEquipmentItemRow
                      key={item.id}
                      item={item}
                      pending={pending}
                      onSave={saveItem}
                      onRemove={removeItem}
                    />
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
