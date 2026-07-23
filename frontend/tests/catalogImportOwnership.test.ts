import assert from "node:assert/strict";
import test from "node:test";

import type { CatalogImportResult } from "../src/features/catalog-import/api/catalogImportApi.ts";
import {
  buildCatalogImportApplyRequest,
  buildCatalogImportPreviewRequest,
  recipeImportOwnershipDescription,
  recipeImportOwnershipLabel,
} from "../src/features/catalog-import/model/catalogImportOwnership.ts";

function preview(overrides: Partial<CatalogImportResult> = {}): CatalogImportResult {
  return {
    kind: "recipes",
    valid: true,
    row_count: 1,
    create_count: 1,
    skip_count: 0,
    component_count: 1,
    note_count: 0,
    ownership_scope: "personal",
    preview_token: "a".repeat(64),
    errors: [],
    ...overrides,
  };
}

test("adds ownership only to Recipe preview requests", () => {
  assert.deepEqual(
    buildCatalogImportPreviewRequest("products", "csv", "personal"),
    { kind: "products", content: "csv" },
  );
  assert.deepEqual(
    buildCatalogImportPreviewRequest("recipes", "csv", "personal"),
    {
      kind: "recipes",
      content: "csv",
      ownership_scope: "personal",
    },
  );
});

test("binds Recipe apply to the matching preview token and scope", () => {
  assert.deepEqual(
    buildCatalogImportApplyRequest(
      "recipes",
      "csv",
      "personal",
      preview(),
    ),
    {
      kind: "recipes",
      content: "csv",
      ownership_scope: "personal",
      preview_token: "a".repeat(64),
    },
  );
  assert.throws(
    () =>
      buildCatalogImportApplyRequest(
        "recipes",
        "csv",
        "club",
        preview(),
      ),
    /no longer matches/,
  );
  assert.throws(
    () =>
      buildCatalogImportApplyRequest(
        "recipes",
        "csv",
        "personal",
        preview({ preview_token: null }),
      ),
    /no longer matches/,
  );
});

test("explains CLUB and PERSONAL outcomes", () => {
  assert.equal(recipeImportOwnershipLabel("club"), "Клубные рецепты");
  assert.equal(recipeImportOwnershipLabel("personal"), "Личные рецепты");
  assert.ok(recipeImportOwnershipDescription("club").includes("опубликованных"));
  assert.ok(recipeImportOwnershipDescription("personal").includes("черновики"));
});
