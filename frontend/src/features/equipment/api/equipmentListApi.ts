import { apiClient } from "@/shared/api/client";

export interface EquipmentListItem {
  id: string;
  equipment_name: string;
  required_quantity: number;
  calculated_quantity: number | null;
  is_manual: boolean;
  is_overridden: boolean;
}

export interface EquipmentList {
  id: string;
  project_id: number;
  meal_plan_id: string;
  status: string;
  items: EquipmentListItem[];
}

export interface EquipmentListItemInput {
  equipment_name: string;
  required_quantity: number;
}

export async function getProjectEquipmentList(
  projectId: number,
): Promise<EquipmentList | null> {
  const response = await apiClient.get<EquipmentList>(
    "/equipment-lists/project/" + projectId,
    { validateStatus: (status) => status === 200 || status === 404 },
  );
  return response.status === 404 ? null : response.data;
}

export async function addProjectEquipmentItem(
  projectId: number,
  input: EquipmentListItemInput,
): Promise<EquipmentListItem> {
  const response = await apiClient.post<EquipmentListItem>(
    `/equipment-lists/project/${projectId}/items`,
    input,
  );
  return response.data;
}

export async function updateProjectEquipmentItem(
  projectId: number,
  itemId: string,
  requiredQuantity: number,
): Promise<EquipmentListItem> {
  const response = await apiClient.put<EquipmentListItem>(
    `/equipment-lists/project/${projectId}/items/${itemId}`,
    { required_quantity: requiredQuantity },
  );
  return response.data;
}

export async function removeProjectEquipmentItem(
  projectId: number,
  itemId: string,
): Promise<void> {
  await apiClient.delete(`/equipment-lists/project/${projectId}/items/${itemId}`);
}
