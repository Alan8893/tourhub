import { isAxiosError } from "axios";

import { apiClient } from "@/shared/api/client";

export interface PurchaseChecklistItem {
  id: string;
  product_id: string;
  product_name: string;
  required_quantity: number;
  purchased_quantity: number;
  remaining_quantity: number;
  unit: string;
  is_checked: boolean;
}

export interface PurchaseChecklist {
  id: string;
  project_id: number | null;
  meal_plan_id: string;
  status: "draft" | "in_progress" | "completed";
  items: PurchaseChecklistItem[];
}

export interface PurchaseChecklistItemUpdate {
  is_checked?: boolean;
  purchased_quantity?: number;
}

export async function getProjectPurchaseChecklist(
  projectId: number,
): Promise<PurchaseChecklist | null> {
  try {
    const response = await apiClient.get<PurchaseChecklist>(
      `/purchase-checklists/project/${projectId}`,
    );
    return response.data;
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function updatePurchaseChecklistItem(
  itemId: string,
  input: PurchaseChecklistItemUpdate,
): Promise<PurchaseChecklistItem> {
  const response = await apiClient.patch<PurchaseChecklistItem>(
    `/purchase-checklists/items/${itemId}`,
    input,
  );
  return response.data;
}
