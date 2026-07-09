import { useMutation } from "@tanstack/react-query";

import { addMealSlotDish } from "../api/mealSlotApi";

export function useAddMealSlotDish() {
  return useMutation({
    mutationFn: ({ slotId, dishId }: { slotId: string; dishId: string }) =>
      addMealSlotDish(slotId, dishId),
  });
}
