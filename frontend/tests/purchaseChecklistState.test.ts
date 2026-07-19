import assert from "node:assert/strict";
import test from "node:test";

import {
  formatPurchaseQuantity,
  getChecklistProgress,
  parsePurchasedQuantity,
  purchaseChecklistResponsiveDirection,
} from "../src/features/purchase/model/purchaseChecklistState.ts";

test("parses non-negative purchased quantities with dot or comma decimals", () => {
  assert.equal(parsePurchasedQuantity(" 125.5 "), 125.5);
  assert.equal(parsePurchasedQuantity("125,5"), 125.5);
  assert.equal(parsePurchasedQuantity("0"), 0);
  assert.equal(parsePurchasedQuantity(""), null);
  assert.equal(parsePurchasedQuantity("-1"), null);
  assert.equal(parsePurchasedQuantity("not-a-number"), null);
});

test("formats purchase quantities without insignificant trailing zeroes", () => {
  assert.equal(formatPurchaseQuantity(500), "500");
  assert.equal(formatPurchaseQuantity(125.5), "125.5");
  assert.equal(formatPurchaseQuantity(1.234), "1.23");
  assert.equal(formatPurchaseQuantity(Number.NaN), "0");
});

test("counts checked purchase items", () => {
  assert.deepEqual(
    getChecklistProgress([
      { is_checked: true },
      { is_checked: false },
      { is_checked: true },
    ]),
    { checked: 2, total: 3 },
  );
});

test("keeps checklist controls stacked until desktop width", () => {
  assert.deepEqual(purchaseChecklistResponsiveDirection, {
    xs: "column",
    md: "row",
  });
});
