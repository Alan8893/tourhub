import { useMutation, useQueryClient } from "@tanstack/react-query";

import { replaceMealSlotDish } from "../api/mealSlotApi";

export function useReplaceMealSlotDish() {
  const queryClient = useQueryClient();

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
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["meal-plan"],
      });
    },
  });
}
