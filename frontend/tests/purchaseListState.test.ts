import assert from "node:assert/strict";
import test from "node:test";

import {
  formatPackageCount,
  formatPurchaseQuantity,
  getPurchaseListSummary,
  purchaseListResponsiveDirection,
} from "../src/features/shopping/model/purchaseListState.ts";

const item = {
  id: "item-1",
  product_id: "product-1",
  product_name: "Рис",
  required_quantity: 1000,
  required_unit: "gram",
  package_size: 400,
  package_unit: "gram",
  packages_count: 3,
  purchase_quantity: 1200,
  surplus_quantity: 200,
};

test("formats purchase quantities and Russian package counts", () => {
  assert.equal(formatPurchaseQuantity(1200, "gram"), "1 200 г");
  assert.equal(formatPurchaseQuantity(1.5, "liter"), "1,5 л");
  assert.equal(formatPackageCount(1), "1 упаковка");
  assert.equal(formatPackageCount(2), "2 упаковки");
  assert.equal(formatPackageCount(5), "5 упаковок");
  assert.equal(formatPackageCount(11), "11 упаковок");
  assert.equal(formatPackageCount(21), "21 упаковка");
});

test("summarizes positions, packages, and surplus lines", () => {
  assert.deepEqual(
    getPurchaseListSummary([
      item,
      {
        ...item,
        id: "item-2",
        packages_count: 1,
        surplus_quantity: 0,
      },
    ]),
    {
      itemsTotal: 2,
      packagesTotal: 4,
      surplusItems: 1,
    },
  );
});

test("uses a stacked package review layout on mobile", () => {
  assert.deepEqual(purchaseListResponsiveDirection, {
    xs: "column",
    sm: "row",
  });
});
