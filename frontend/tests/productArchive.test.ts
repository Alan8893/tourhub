import assert from "node:assert/strict";
import test from "node:test";

import type { ArchivedProduct } from "../src/features/recipe/api/productArchiveApi.ts";
import {
  canRestoreArchivedProduct,
  productArchiveNotice,
} from "../src/features/recipe/model/productArchive.ts";

function product(overrides: Partial<ArchivedProduct> = {}): ArchivedProduct {
  return {
    id: "product-1",
    name: "Гречка",
    category: "Крупы",
    unit: "gram",
    package_size: 800,
    is_archived: true,
    archived_by_alcohol_policy: false,
    ...overrides,
  };
}

test("allows restore only for manually archived products", () => {
  assert.equal(canRestoreArchivedProduct(product()), true);
  assert.equal(
    canRestoreArchivedProduct(product({ archived_by_alcohol_policy: true })),
    false,
  );
  assert.equal(canRestoreArchivedProduct(product({ is_archived: false })), false);
});

test("explains central policy lock without exposing internal data", () => {
  assert.equal(productArchiveNotice(product()), null);
  const notice = productArchiveNotice(product({ archived_by_alcohol_policy: true }));
  assert.ok(notice?.includes("алкогольные позиции"));
  assert.equal(notice?.toLowerCase().includes("token"), false);
  assert.equal(notice?.toLowerCase().includes("cookie"), false);
});
