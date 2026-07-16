export const purchaseChecklistResponsiveDirection = {
  xs: "column",
  sm: "row",
} as const;

export function formatPurchaseQuantity(value: number): string {
  if (!Number.isFinite(value)) {
    return "0";
  }
  return Number(value.toFixed(2)).toString();
}

export function parsePurchasedQuantity(value: string): number | null {
  const normalized = value.trim().replace(",", ".");
  if (!normalized) {
    return null;
  }

  const quantity = Number(normalized);
  if (!Number.isFinite(quantity) || quantity < 0) {
    return null;
  }
  return quantity;
}

export function getChecklistProgress(
  items: ReadonlyArray<{ is_checked: boolean }>,
): { checked: number; total: number } {
  return {
    checked: items.filter((item) => item.is_checked).length,
    total: items.length,
  };
}
