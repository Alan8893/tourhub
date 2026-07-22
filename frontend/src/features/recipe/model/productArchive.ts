import type { ArchivedProduct } from "../api/productArchiveApi";

export function canRestoreArchivedProduct(product: ArchivedProduct): boolean {
  return product.is_archived && !product.archived_by_alcohol_policy;
}

export function productArchiveNotice(product: ArchivedProduct): string | null {
  if (product.archived_by_alcohol_policy) {
    return "Восстановление запрещено центральной политикой: алкогольные позиции не возвращаются в каталог.";
  }
  return null;
}
