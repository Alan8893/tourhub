import type { CatalogImportKind, CatalogImportResult } from "../api/catalogImportApi";

export const catalogImportTemplates: Record<CatalogImportKind, string> = {
  products: [
    "name;category;unit;package_size",
    "Гречка;Крупы;gram;800",
    "Тушёнка;Консервы;can;1",
  ].join("\n"),
  recipes: [
    "recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority",
    "Походная гречка;Гречка;base;80;gram;per_person;;cooking_tip;Промыть крупу;10",
    "Походная гречка;Тушёнка;cooking;1;can;package_per_people;4;expedition_tip;Открыть перед подачей;20",
  ].join("\n"),
};

export function getCatalogImportFilename(kind: CatalogImportKind): string {
  return kind === "products" ? "tourhub-products-template.csv" : "tourhub-recipes-template.csv";
}

export function getCatalogImportSummary(result: CatalogImportResult): string {
  if (result.kind === "products") {
    return `Строк: ${result.row_count}. Будет создано: ${result.create_count}. Пропущено существующих: ${result.skip_count}.`;
  }
  return `Строк компонентов: ${result.row_count}. Рецептов: ${result.create_count}. Компонентов: ${result.component_count}. Заметок: ${result.note_count}.`;
}
