import assert from "node:assert/strict";
import test from "node:test";

import {
  getEquipmentSummary,
  isCampItemInputValid,
  normalizeCampItemName,
  parseCampItemQuantity,
} from "../src/features/equipment/model/campItemState.ts";

test("equipment name normalization", () => {
  assert.equal(normalizeCampItemName("  Camp   pot "), "Camp pot");
});

test("equipment quantity parsing", () => {
  assert.equal(parseCampItemQuantity("3"), 3);
  assert.equal(parseCampItemQuantity("0"), null);
  assert.equal(parseCampItemQuantity("1.5"), null);
});

test("equipment input validation", () => {
  assert.equal(isCampItemInputValid("Stove", "2"), true);
  assert.equal(isCampItemInputValid(" ", "2"), false);
});

test("equipment summary", () => {
  const items = [
    { id: "1", equipment_name: "Pot", required_quantity: 3 },
    { id: "2", equipment_name: "Stove", required_quantity: 1 },
  ];
  assert.deepEqual(getEquipmentSummary(items), { positions: 2, totalUnits: 4 });
});
