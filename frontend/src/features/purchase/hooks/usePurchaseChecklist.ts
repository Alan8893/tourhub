import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getProjectPurchaseChecklist,
  PurchaseChecklistItemUpdate,
  updatePurchaseChecklistItem,
} from "../api/purchaseChecklistApi";

export function useProjectPurchaseChecklist(
  projectId: number,
  refreshKey?: string,
) {
  return useQuery({
    queryKey: ["purchase-checklist", projectId, refreshKey ?? "stored"],
    queryFn: () => getProjectPurchaseChecklist(projectId),
    enabled: Number.isInteger(projectId) && projectId > 0,
    retry: false,
  });
}

export function useUpdatePurchaseChecklistItem(projectId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      itemId,
      input,
    }: {
      itemId: string;
      input: PurchaseChecklistItemUpdate;
    }) => updatePurchaseChecklistItem(itemId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["purchase-checklist", projectId],
      });
    },
  });
}
