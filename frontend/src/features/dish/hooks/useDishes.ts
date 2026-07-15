import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createDish,
  getDish,
  getDishCatalogueReadiness,
  getDishes,
  updateDish,
  updateDishMealRoles,
  type DishMealRolesWriteInput,
  type DishWriteInput,
} from "../api/dishApi";

export function useDishes() {
  return useQuery({ queryKey: ["dishes"], queryFn: getDishes });
}

export function useDishCatalogueReadiness() {
  return useQuery({
    queryKey: ["dishes", "catalogue-readiness"],
    queryFn: getDishCatalogueReadiness,
  });
}

export function useDish(dishId: string | undefined) {
  return useQuery({
    queryKey: ["dishes", dishId],
    queryFn: () => getDish(dishId!),
    enabled: Boolean(dishId),
  });
}

function useInvalidateDishes() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["dishes"] });
}

export function useCreateDish() {
  const invalidate = useInvalidateDishes();
  return useMutation({ mutationFn: createDish, onSuccess: invalidate });
}

export function useUpdateDish() {
  const invalidate = useInvalidateDishes();
  return useMutation({
    mutationFn: ({ dishId, input }: { dishId: string; input: DishWriteInput }) =>
      updateDish(dishId, input),
    onSuccess: invalidate,
  });
}

export function useUpdateDishMealRoles() {
  const invalidate = useInvalidateDishes();
  return useMutation({
    mutationFn: ({ dishId, input }: { dishId: string; input: DishMealRolesWriteInput }) =>
      updateDishMealRoles(dishId, input),
    onSuccess: invalidate,
  });
}
