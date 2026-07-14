import assert from "node:assert/strict";
import test from "node:test";

import {
  getCatalogImportFilename,
  getCatalogImportTemplate,
} from "../src/features/catalog-import/model/catalogImportTemplates.ts";

test("product template contains required headers", () => {
  const template = getCatalogImportTemplate("products");
  assert.match(template, /^name;category;unit;package_size/m);
  assert.equal(getCatalogImportFilename("products"), "tourhub-products-template.csv");
});

test("recipe template contains components and note headers", () => {
  const template = getCatalogImportTemplate("recipes");
  assert.match(template, /recipe_name;product_name;component_type;amount/);
  assert.match(template, /note_type;note_text;note_priority/);
  assert.equal(getCatalogImportFilename("recipes"), "tourhub-recipes-template.csv");
});
