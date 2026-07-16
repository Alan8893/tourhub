import type { PurchaseListItem } from "../api/purchaseListApi";

const unitLabels: Record<string, string> = {
  gram: "г",
  kilogram: "кг",
  milliliter: "мл",
  liter: "л",
  piece: "шт.",
};

export const purchaseListResponsiveDirection = {
  xs: "column",
  sm: "row",
} as const;

export function formatPurchaseQuantity(value: number, unit: string): string {
  const quantity = new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 2,
  })
    .format(value)
    .replace(/[\u00a0\u202f]/g, " ");
  return `${quantity} ${unitLabels[unit] ?? unit}`;
}

export function formatPackageCount(count: number): string {
  const mod100 = count % 100;
  const mod10 = count % 10;
  if (mod100 >= 11 && mod100 <= 14) return `${count} упаковок`;
  if (mod10 === 1) return `${count} упаковка`;
  if (mod10 >= 2 && mod10 <= 4) return `${count} упаковки`;
  return `${count} упаковок`;
}

export function getPurchaseListSummary(items: PurchaseListItem[]) {
  return {
    itemsTotal: items.length,
    packagesTotal: items.reduce((total, item) => total + item.packages_count, 0),
    surplusItems: items.filter((item) => item.surplus_quantity > 0).length,
  };
}
