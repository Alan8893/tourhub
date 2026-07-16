import { useQuery } from "@tanstack/react-query";

import { getProjectPurchaseList } from "../api/purchaseListApi";

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
