import type { EquipmentListItem } from "../api/equipmentListApi";

export function normalizeCampItemName(value: string): string {
  return value.trim().replace(/\s+/g, " ");
}

export function parseCampItemQuantity(value: string): number | null {
  if (!/^\d+$/.test(value.trim())) return null;
  const quantity = Number(value);
  return Number.isSafeInteger(quantity) && quantity > 0 && quantity <= 9999
    ? quantity
    : null;
}

export function isCampItemInputValid(name: string, quantity: string): boolean {
  return (
    normalizeCampItemName(name).length > 0 &&
    normalizeCampItemName(name).length <= 255 &&
    parseCampItemQuantity(quantity) !== null
  );
}

export function getEquipmentSummary(items: EquipmentListItem[]) {
  return {
    positions: items.length,
    totalUnits: items.reduce((total, item) => total + item.required_quantity, 0),
  };
}
