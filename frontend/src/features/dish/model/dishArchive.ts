import type { ArchivedDish } from "../api/dishArchiveApi";

export function canRestoreArchivedDish(dish: ArchivedDish): boolean {
  return dish.is_archived && !dish.archived_by_alcohol_policy;
}

export function dishArchiveNotice(dish: ArchivedDish): string | null {
  if (dish.archived_by_alcohol_policy) {
    return "Восстановление запрещено центральной политикой: блюда с алкогольными ссылками не возвращаются в каталог.";
  }
  return null;
}
