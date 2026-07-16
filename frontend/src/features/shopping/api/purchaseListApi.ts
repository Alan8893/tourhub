import { apiClient } from "@/shared/api/client";

export interface PurchaseListItem {
  id: string;
  product_id: string;
  product_name: string;
  required_quantity: number;
  required_unit: string;
  package_size: number;
  package_unit: string;
  packages_count: number;
  purchase_quantity: number;
  surplus_quantity: number;
}

export interface PurchaseList {
  id: string;
  project_id: number | null;
  meal_plan_id: string;
  status: string;
  items: PurchaseListItem[];
}

export async function getProjectPurchaseList(projectId: number): Promise<PurchaseList> {
  const response = await apiClient.get<PurchaseList>(
    `/purchase-lists/project/${projectId}`,
  );
  return response.data;
}
