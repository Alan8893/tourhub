import type {
  DishCatalogueCoverage,
  DishCatalogueReadiness,
  MealRole,
  MealType,
} from "../api/dishApi";

const MEAL_TYPE_LABELS: Record<MealType, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

const ROLE_LABELS: Record<MealRole, string> = {
  main: "основное блюдо",
  addition: "дополнение",
  drink: "напиток",
  snack: "блюдо для перекуса",
};

export function getMissingRequiredCoverage(
  readiness: DishCatalogueReadiness,
): DishCatalogueCoverage[] {
  return readiness.coverage.filter((item) => item.required && !item.ready);
}

export function getMissingRecommendedCoverage(
  readiness: DishCatalogueReadiness,
): DishCatalogueCoverage[] {
  return readiness.coverage.filter((item) => !item.required && !item.ready);
}

export function formatCoverageGap(item: DishCatalogueCoverage): string {
  return `${MEAL_TYPE_LABELS[item.meal_type]}: нужно добавить ${ROLE_LABELS[item.role]}.`;
}

export function formatRecommendationGap(item: DishCatalogueCoverage): string {
  return `${MEAL_TYPE_LABELS[item.meal_type]}: желательно добавить ${ROLE_LABELS[item.role]}.`;
}

export function formatClassificationSummary(readiness: DishCatalogueReadiness): string {
  if (readiness.active_dish_count === 0) return "В каталоге нет активных блюд.";
  if (readiness.unclassified_dish_count === 0) {
    return `Все активные блюда классифицированы: ${readiness.classified_dish_count}.`;
  }
  return `Без ролей осталось блюд: ${readiness.unclassified_dish_count} из ${readiness.active_dish_count}.`;
}
