import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { archiveProduct, getArchivedProducts, restoreProduct } from "../api/productArchiveApi";

export function useArchivedProducts(enabled: boolean) {
  return useQuery({
    queryKey: ["recipe-products", "archived"],
    queryFn: getArchivedProducts,
    enabled,
  });
}

function useInvalidateProductCatalogue() {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: ["recipe-products"] });
}

export function useArchiveProduct() {
  const invalidate = useInvalidateProductCatalogue();
  return useMutation({ mutationFn: archiveProduct, onSuccess: invalidate });
}

export function useRestoreProduct() {
  const invalidate = useInvalidateProductCatalogue();
  return useMutation({ mutationFn: restoreProduct, onSuccess: invalidate });
}
