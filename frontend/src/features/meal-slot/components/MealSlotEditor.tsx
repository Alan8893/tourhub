import { useState } from "react";

import { Alert, Button, Stack, Typography } from "@mui/material";

import {
  useAddMealSlotDish,
  useRemoveMealSlotDish,
  useReplaceMealSlotDish,
  DishSelector,
} from "@/features/meal-slot";
import {
  canSubmitDishSelection,
  createAddMealSlotDishCommand,
  createRemoveMealSlotDishCommand,
  createReplaceMealSlotDishCommand,
  hasMealSlotMutationError,
  isMealSlotMutationBusy,
} from "@/features/meal-slot/model/mealSlotEditorState";

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

  return (
    <Stack spacing={1}>
      <Typography variant="subtitle1">{mealType}</Typography>

      {mutationError && (
        <Alert severity="error">
          Не удалось изменить состав приёма пищи. Повторите попытку.
        </Alert>
      )}

      {dishes.map((dish) => {
        const replacementId = replaceDishId[dish.id] ?? "";

        return (
          <Stack key={dish.id} direction="row" spacing={1} alignItems="center">
            <Typography sx={{ flex: 1 }}>
              {dish.dish_name ?? dish.dish_id}
            </Typography>

            <DishSelector
              value={replacementId}
              onChange={(value) =>
                setReplaceDishId((current) => ({
                  ...current,
                  [dish.id]: value,
                }))
              }
            />

            <Button
              size="small"
              disabled={!canSubmitDishSelection(replacementId, busy)}
              onClick={() =>
                replaceMutation.mutate(
                  createReplaceMealSlotDishCommand(slotId, dish.id, replacementId),
                )
              }
            >
              Заменить
            </Button>

            <Button
              size="small"
              disabled={busy}
              onClick={() =>
                removeMutation.mutate(
                  createRemoveMealSlotDishCommand(slotId, dish.id),
                  {
                    onSuccess: () => {
                      setReplaceDishId((current) => {
                        const next = { ...current };
                        delete next[dish.id];
                        return next;
                      });
                    },
                  },
                )
              }
            >
              Удалить
            </Button>
          </Stack>
        );
      })}

      <Stack direction="row" spacing={1} alignItems="center">
        <DishSelector value={newDishId} onChange={setNewDishId} />

        <Button
          disabled={!canSubmitDishSelection(newDishId, busy)}
          onClick={() =>
            addMutation.mutate(createAddMealSlotDishCommand(slotId, newDishId), {
              onSuccess: () => setNewDishId(""),
            })
          }
        >
          Добавить блюдо
        </Button>
      </Stack>
    </Stack>
  );
}
