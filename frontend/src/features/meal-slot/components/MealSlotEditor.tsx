import { useState } from "react";

import {
  Alert,
  Button,
  Chip,
  Collapse,
  Divider,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";

import DishSelector from "./DishSelector";
import { useAddMealSlotDish } from "../hooks/useAddMealSlotDish";
import { useRemoveMealSlotDish } from "../hooks/useRemoveMealSlotDish";
import { useReplaceMealSlotDish } from "../hooks/useReplaceMealSlotDish";
import {
  canSubmitDishSelection,
  createAddMealSlotDishCommand,
  createRemoveMealSlotDishCommand,
  createReplaceMealSlotDishCommand,
  formatDishCount,
  getMealSlotSuccessMessage,
  hasMealSlotMutationError,
  isMealSlotMutationBusy,
  mealSlotResponsiveDirection,
} from "../model/mealSlotEditorState";

interface MealSlotDish {
  id: string;
  dish_id: string;
  dish_name?: string;
}

interface MealSlotEditorProps {
  slotId: string;
  mealType: string;
  dishes: MealSlotDish[];
}

export default function MealSlotEditor({
  slotId,
  mealType,
  dishes,
}: MealSlotEditorProps) {
  const addMutation = useAddMealSlotDish();
  const removeMutation = useRemoveMealSlotDish();
  const replaceMutation = useReplaceMealSlotDish();

  const [newDishId, setNewDishId] = useState("");
  const [replaceDishId, setReplaceDishId] = useState<Record<string, string>>({});
  const [activeReplacementId, setActiveReplacementId] = useState<string | null>(null);
  const [pendingRemovalId, setPendingRemovalId] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const mutationState = {
    addPending: addMutation.isPending,
    replacePending: replaceMutation.isPending,
    removePending: removeMutation.isPending,
    addError: addMutation.isError,
    replaceError: replaceMutation.isError,
    removeError: removeMutation.isError,
  };
  const busy = isMealSlotMutationBusy(mutationState);
  const mutationError = hasMealSlotMutationError(mutationState);

  const clearMutationFeedback = () => {
    addMutation.reset();
    replaceMutation.reset();
    removeMutation.reset();
    setSuccessMessage(null);
  };

  const openReplacement = (slotDishId: string) => {
    clearMutationFeedback();
    setPendingRemovalId(null);
    setIsAdding(false);
    setActiveReplacementId(slotDishId);
  };

  const openRemovalConfirmation = (slotDishId: string) => {
    clearMutationFeedback();
    setActiveReplacementId(null);
    setIsAdding(false);
    setPendingRemovalId(slotDishId);
  };

  return (
    <Paper variant="outlined" sx={{ p: { xs: 1.25, sm: 1.5 } }}>
      <Stack spacing={1.25}>
        <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
          <Typography variant="subtitle1" component="h4">
            {mealType}
          </Typography>
          <Chip size="small" variant="outlined" label={formatDishCount(dishes.length)} />
        </Stack>

        {successMessage && (
          <Alert severity="success" role="status" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        {mutationError && (
          <Alert severity="error" role="alert">
            Не удалось изменить состав приёма пищи. Проверьте соединение и повторите попытку.
          </Alert>
        )}

        {dishes.length === 0 && (
          <Typography variant="body2" color="text.secondary">
            В этом приёме пищи пока нет блюд.
          </Typography>
        )}

        {dishes.map((dish) => {
          const dishName = dish.dish_name ?? dish.dish_id;
          const replacementId = replaceDishId[dish.id] ?? "";
          const replacementOpen = activeReplacementId === dish.id;
          const removalOpen = pendingRemovalId === dish.id;

          return (
            <Paper key={dish.id} variant="outlined" sx={{ p: 1 }}>
              <Stack spacing={1}>
                <Stack
                  direction={mealSlotResponsiveDirection}
                  spacing={1}
                  alignItems={{ xs: "stretch", sm: "center" }}
                >
                  <Typography
                    variant="body2"
                    title={dishName}
                    sx={{ flex: 1, minWidth: 0, overflowWrap: "anywhere" }}
                  >
                    {dishName}
                  </Typography>

                  <Stack direction="row" spacing={0.5} justifyContent={{ xs: "flex-end", sm: "initial" }}>
                    <Tooltip title="Выбрать другое блюдо">
                      <span>
                        <Button
                          size="small"
                          disabled={busy}
                          aria-label={`Заменить блюдо «${dishName}»`}
                          onClick={() => openReplacement(dish.id)}
                        >
                          Заменить
                        </Button>
                      </span>
                    </Tooltip>
                    <Tooltip title="Удаление потребует подтверждения">
                      <span>
                        <Button
                          size="small"
                          color="error"
                          disabled={busy}
                          aria-label={`Удалить блюдо «${dishName}»`}
                          onClick={() => openRemovalConfirmation(dish.id)}
                        >
                          Удалить
                        </Button>
                      </span>
                    </Tooltip>
                  </Stack>
                </Stack>

                <Collapse in={replacementOpen} unmountOnExit>
                  <Stack
                    direction={mealSlotResponsiveDirection}
                    spacing={1}
                    alignItems={{ xs: "stretch", sm: "center" }}
                  >
                    <DishSelector
                      value={replacementId}
                      label="Новое блюдо"
                      fullWidth
                      disabled={busy}
                      onChange={(value) =>
                        setReplaceDishId((current) => ({
                          ...current,
                          [dish.id]: value,
                        }))
                      }
                    />
                    <Stack direction="row" spacing={1} justifyContent="flex-end">
                      <Button
                        variant="contained"
                        size="small"
                        disabled={!canSubmitDishSelection(replacementId, busy)}
                        onClick={() => {
                          clearMutationFeedback();
                          replaceMutation.mutate(
                            createReplaceMealSlotDishCommand(slotId, dish.id, replacementId),
                            {
                              onSuccess: () => {
                                setReplaceDishId((current) => {
                                  const next = { ...current };
                                  delete next[dish.id];
                                  return next;
                                });
                                setActiveReplacementId(null);
                                setSuccessMessage(getMealSlotSuccessMessage("replace"));
                              },
                            },
                          );
                        }}
                      >
                        Сохранить
                      </Button>
                      <Button
                        size="small"
                        disabled={busy}
                        onClick={() => setActiveReplacementId(null)}
                      >
                        Отмена
                      </Button>
                    </Stack>
                  </Stack>
                </Collapse>

                <Collapse in={removalOpen} unmountOnExit>
                  <Alert severity="warning">
                    <Stack
                      direction={mealSlotResponsiveDirection}
                      spacing={1}
                      alignItems={{ xs: "stretch", sm: "center" }}
                    >
                      <Typography variant="body2" sx={{ flex: 1 }}>
                        Удалить блюдо «{dishName}» из этого приёма пищи?
                      </Typography>
                      <Stack direction="row" spacing={1} justifyContent="flex-end">
                        <Button
                          size="small"
                          variant="contained"
                          color="error"
                          disabled={busy}
                          onClick={() => {
                            clearMutationFeedback();
                            removeMutation.mutate(
                              createRemoveMealSlotDishCommand(slotId, dish.id),
                              {
                                onSuccess: () => {
                                  setReplaceDishId((current) => {
                                    const next = { ...current };
                                    delete next[dish.id];
                                    return next;
                                  });
                                  setPendingRemovalId(null);
                                  setSuccessMessage(getMealSlotSuccessMessage("remove"));
                                },
                              },
                            );
                          }}
                        >
                          Да, удалить
                        </Button>
                        <Button
                          size="small"
                          disabled={busy}
                          onClick={() => setPendingRemovalId(null)}
                        >
                          Отмена
                        </Button>
                      </Stack>
                    </Stack>
                  </Alert>
                </Collapse>
              </Stack>
            </Paper>
          );
        })}

        <Divider />

        {!isAdding ? (
          <Button
            variant="outlined"
            disabled={busy}
            sx={{ alignSelf: { xs: "stretch", sm: "flex-start" } }}
            onClick={() => {
              clearMutationFeedback();
              setActiveReplacementId(null);
              setPendingRemovalId(null);
              setIsAdding(true);
            }}
          >
            Добавить блюдо
          </Button>
        ) : (
          <Paper variant="outlined" sx={{ p: 1 }}>
            <Stack
              direction={mealSlotResponsiveDirection}
              spacing={1}
              alignItems={{ xs: "stretch", sm: "center" }}
            >
              <DishSelector
                value={newDishId}
                label="Блюдо для добавления"
                fullWidth
                disabled={busy}
                onChange={setNewDishId}
              />
              <Stack direction="row" spacing={1} justifyContent="flex-end">
                <Button
                  variant="contained"
                  size="small"
                  disabled={!canSubmitDishSelection(newDishId, busy)}
                  onClick={() => {
                    clearMutationFeedback();
                    addMutation.mutate(createAddMealSlotDishCommand(slotId, newDishId), {
                      onSuccess: () => {
                        setNewDishId("");
                        setIsAdding(false);
                        setSuccessMessage(getMealSlotSuccessMessage("add"));
                      },
                    });
                  }}
                >
                  Добавить
                </Button>
                <Button
                  size="small"
                  disabled={busy}
                  onClick={() => {
                    setNewDishId("");
                    setIsAdding(false);
                  }}
                >
                  Отмена
                </Button>
              </Stack>
            </Stack>
          </Paper>
        )}
      </Stack>
    </Paper>
  );
}
