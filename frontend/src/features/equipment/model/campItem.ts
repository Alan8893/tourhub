export interface CampItem {
  id: string;
  equipment_name: string;
  quantity: number;
}

export type CampItemInput = Omit<CampItem, "id">;
export type CampItemList = { items: CampItem[] };
