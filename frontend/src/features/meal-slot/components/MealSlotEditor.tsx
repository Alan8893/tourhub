import { Button, Stack, Typography } from "@mui/material";

import {
  useAddMealSlotDish,
  useRemoveMealSlotDish,
  useReplaceMealSlotDish,
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

  return (
    <Stack spacing={1}>
      <Typography variant="subtitle1">{mealType}</Typography>

      {dishes.map((dish) => (
        <Stack key={dish.id} direction="row" spacing={1}>
          <Typography sx={{ flex: 1 }}>
            {dish.dish_name ?? dish.dish_id}
          </Typography>

          <Button
            size="small"
            onClick={() =>
              replaceMutation.mutate({
                slotId,
                slotDishId: dish.id,
                dishId: "replace-dish-id",
              })
            }
          >
            Replace
          </Button>

          <Button
            size="small"
            onClick={() =>
              removeMutation.mutate({
                slotId,
                slotDishId: dish.id,
              })
            }
          >
            Remove
          </Button>
        </Stack>
      ))}

      <Button
        onClick={() =>
          addMutation.mutate({
            slotId,
            dishId: "new-dish-id",
          })
        }
      >
        Add dish
      </Button>
    </Stack>
  );
}
