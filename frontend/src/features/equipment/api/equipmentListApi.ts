import { apiClient } from "@/shared/api/client";

export interface EquipmentListItem {
  id: string;
  equipment_name: string;
  required_quantity: number;
}

export interface EquipmentList {
  id: string;
  project_id: number;
  meal_plan_id: string;
  status: string;
  items: EquipmentListItem[];
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
