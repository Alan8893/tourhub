import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { archiveDish, getArchivedDishes, restoreDish } from "../api/dishArchiveApi";

export function useArchivedDishes(enabled: boolean) {
  return useQuery({
    queryKey: ["dishes", "archived"],
    queryFn: getArchivedDishes,
    enabled,
  });
}

function useInvalidateDishCatalogue() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["dishes"] });
}

export function useArchiveDish() {
  const invalidate = useInvalidateDishCatalogue();
  return useMutation({ mutationFn: archiveDish, onSuccess: invalidate });
}

export function useRestoreDish() {
  const invalidate = useInvalidateDishCatalogue();
  return useMutation({ mutationFn: restoreDish, onSuccess: invalidate });
}
