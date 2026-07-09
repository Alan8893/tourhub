import { useMutation } from "@tanstack/react-query";

import { replaceMealSlotDish } from "../api/mealSlotApi";

export function useReplaceMealSlotDish() {
  return useMutation({
    mutationFn: ({
      slotId,
      slotDishId,
      dishId,
    }: {
      slotId: string;
      slotDishId: string;
      dishId: string;
    }) => replaceMealSlotDish(slotId, slotDishId, dishId),
  });
}
