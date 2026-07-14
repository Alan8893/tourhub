import assert from "node:assert/strict";
import test from "node:test";

import {
  catalogImportTemplates,
  getCatalogImportFilename,
  getCatalogImportSummary,
} from "../src/features/catalog-import/model/catalogImport.ts";

test("provides Excel-friendly semicolon CSV templates", () => {
  assert.match(catalogImportTemplates.products, /^name;category;unit;package_size/);
  assert.match(catalogImportTemplates.recipes, /^recipe_name;product_name;component_type/);
  assert.equal(getCatalogImportFilename("products"), "tourhub-products-template.csv");
  assert.equal(getCatalogImportFilename("recipes"), "tourhub-recipes-template.csv");
});

test("formats product and recipe preview summaries", () => {
  assert.equal(
    getCatalogImportSummary({
      kind: "products",
      valid: true,
      row_count: 3,
      create_count: 2,
      skip_count: 1,
      component_count: 0,
      note_count: 0,
      errors: [],
    }),
    "Строк: 3. Будет создано: 2. Пропущено существующих: 1.",
  );

  assert.equal(
    getCatalogImportSummary({
      kind: "recipes",
      valid: true,
      row_count: 4,
      create_count: 2,
      skip_count: 0,
      component_count: 4,
      note_count: 1,
      errors: [],
    }),
    "Строк компонентов: 4. Рецептов: 2. Компонентов: 4. Заметок: 1.",
  );
});
