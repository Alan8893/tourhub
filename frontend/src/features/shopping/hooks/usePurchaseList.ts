import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  getProjectPurchaseList,
  PurchaseListUpdate,
  updatePurchaseList,
} from "../api/purchaseListApi";

export function useProjectPurchaseList(
  projectId: number,
  refreshKey?: string,
) {
  return useQuery({
    queryKey: ["purchase-list", projectId, refreshKey ?? "stored"],
    queryFn: () => getProjectPurchaseList(projectId),
    enabled: Number.isInteger(projectId) && projectId > 0,
    retry: false,
  });
}

export function useUpdatePurchaseList(projectId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      purchaseListId,
      input,
    }: {
      purchaseListId: string;
      input: PurchaseListUpdate;
    }) => updatePurchaseList(purchaseListId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["purchase-list", projectId],
      });
    },
  });
}
