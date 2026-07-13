import { useMutation, useQueryClient } from "@tanstack/react-query";

import { removeMealSlotDish } from "../api/mealSlotApi";

export function useRemoveMealSlotDish() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slotId, slotDishId }: { slotId: string; slotDishId: string }) =>
      removeMealSlotDish(slotId, slotDishId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["meal-plan"],
      });
    },
  });
}
