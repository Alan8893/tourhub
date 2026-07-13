import { useMutation, useQueryClient } from "@tanstack/react-query";

import { addMealSlotDish } from "../api/mealSlotApi";

export function useAddMealSlotDish() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slotId, dishId }: { slotId: string; dishId: string }) =>
      addMealSlotDish(slotId, dishId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["meal-plan"],
      });
    },
  });
}
