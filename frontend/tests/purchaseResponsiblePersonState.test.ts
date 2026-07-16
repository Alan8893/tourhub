import assert from "node:assert/strict";
import test from "node:test";

import {
  getResponsiblePersonSuccessMessage,
  isResponsiblePersonValid,
  normalizeResponsiblePerson,
  responsiblePersonMaxLength,
} from "../src/features/shopping/model/purchaseResponsiblePersonState.ts";

test("normalizes and clears responsible person values", () => {
  assert.equal(normalizeResponsiblePerson("  Анна Петрова  "), "Анна Петрова");
  assert.equal(normalizeResponsiblePerson("   "), null);
});

test("validates the persisted length limit", () => {
  assert.equal(isResponsiblePersonValid("А".repeat(responsiblePersonMaxLength)), true);
  assert.equal(isResponsiblePersonValid("А".repeat(responsiblePersonMaxLength + 1)), false);
});

test("returns explicit save and clear feedback", () => {
  assert.equal(getResponsiblePersonSuccessMessage("Анна"), "Ответственный сохранён.");
  assert.equal(getResponsiblePersonSuccessMessage("  "), "Ответственный удалён.");
});
