import { useMemo, useState } from "react";

import { Button, Stack, Typography } from "@mui/material";

import {
  useAddMealSlotDish,
  useRemoveMealSlotDish,
  useReplaceMealSlotDish,
  DishSelector,
} from "@/features/meal-slot";

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

  const busy = addMutation.isPending || removeMutation.isPending || replaceMutation.isPending;

  const canAdd = useMemo(() => newDishId.trim().length > 0, [newDishId]);

  return (
    <Stack spacing={1}>
      <Typography variant="subtitle1">{mealType}</Typography>

      {dishes.map((dish) => (
        <Stack key={dish.id} direction="row" spacing={1} alignItems="center">
          <Typography sx={{ flex: 1 }}>
            {dish.dish_name ?? dish.dish_id}
          </Typography>

          <DishSelector
            value={replaceDishId[dish.id] ?? ""}
            onChange={(value) =>
              setReplaceDishId((current) => ({
                ...current,
                [dish.id]: value,
              }))
            }
          />

          <Button
            size="small"
            disabled={busy || !replaceDishId[dish.id]}
            onClick={() =>
              replaceMutation.mutate({
                slotId,
                slotDishId: dish.id,
                dishId: replaceDishId[dish.id],
              })
            }
          >
            Replace
          </Button>

          <Button
            size="small"
            disabled={busy}
            onClick={() =>
              removeMutation.mutate(
                {
                  slotId,
                  slotDishId: dish.id,
                },
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
            Remove
          </Button>
        </Stack>
      ))}

      <Stack direction="row" spacing={1} alignItems="center">
        <DishSelector value={newDishId} onChange={setNewDishId} />

        <Button
          disabled={busy || !canAdd}
          onClick={() =>
            addMutation.mutate(
              {
                slotId,
                dishId: newDishId,
              },
              {
                onSuccess: () => setNewDishId(""),
              },
            )
          }
        >
          Add dish
        </Button>
      </Stack>
    </Stack>
  );
}
