import type { CatalogImportKind } from "../api/catalogImportApi";

const productTemplate = `name;category;unit;package_size
Гречка;Крупы;gram;800
Тушёнка;Консервы;can;1
`;

const recipeTemplate = `recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority
Походная каша;Гречка;base;80;gram;per_person;;;Промыть крупу;10
Походная каша;Тушёнка;cooking;1;can;package_per_people;4;expedition_tip;Открывать перед подачей;20
`;

export function getCatalogImportTemplate(kind: CatalogImportKind): string {
  return kind === "products" ? productTemplate : recipeTemplate;
}

export function getCatalogImportFilename(kind: CatalogImportKind): string {
  return kind === "products" ? "tourhub-products-template.csv" : "tourhub-recipes-template.csv";
}
