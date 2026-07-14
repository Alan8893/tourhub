import assert from "node:assert/strict";
import test from "node:test";

import {
  toProductWriteInput,
  toRecipeNoteWriteInput,
  validateProductDraft,
  validateRecipeNoteDraft,
} from "../src/features/recipe/model/recipeNotesProducts.ts";

test("normalizes recipe notes", () => {
  const draft = {
    type: "serving_tip" as const,
    text: "  Подавать горячим  ",
    priority: "20",
  };
  assert.equal(validateRecipeNoteDraft(draft), null);
  assert.deepEqual(toRecipeNoteWriteInput(draft), {
    type: "serving_tip",
    text: "Подавать горячим",
    priority: 20,
  });
});

test("rejects invalid recipe notes", () => {
  assert.equal(
    validateRecipeNoteDraft({ type: "cooking_tip", text: " ", priority: "100" }),
    "Введите текст заметки.",
  );
  assert.equal(
    validateRecipeNoteDraft({ type: "cooking_tip", text: "Текст", priority: "-1" }),
    "Приоритет должен быть целым неотрицательным числом.",
  );
});

test("normalizes products", () => {
  const draft = {
    name: "  Рис  ",
    category: "  Крупы ",
    unit: " gram ",
    packageSize: "900",
  };
  assert.equal(validateProductDraft(draft), null);
  assert.deepEqual(toProductWriteInput(draft), {
    name: "Рис",
    category: "Крупы",
    unit: "gram",
    package_size: 900,
  });
});

test("rejects invalid product package size", () => {
  assert.equal(
    validateProductDraft({ name: "Рис", category: "", unit: "gram", packageSize: "0" }),
    "Размер упаковки должен быть положительным целым числом.",
  );
});
