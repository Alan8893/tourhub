import { useMutation } from "@tanstack/react-query";

import { removeMealSlotDish } from "../api/mealSlotApi";

export function useRemoveMealSlotDish() {
  return useMutation({
    mutationFn: ({ slotId, slotDishId }: { slotId: string; slotDishId: string }) =>
      removeMealSlotDish(slotId, slotDishId),
  });
}
