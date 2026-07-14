import assert from "node:assert/strict";
import test from "node:test";

import {
  toRecipeComponentWriteInput,
  validateRecipeComponentDraft,
  validateRecipeName,
} from "../src/features/recipe/model/recipeEditor.ts";

const validDraft = {
  productId: "product-1",
  componentType: "base" as const,
  amount: "80",
  unit: "gram",
  calculationType: "per_person" as const,
  peopleCount: "",
};

test("requires a non-empty recipe name", () => {
  assert.equal(validateRecipeName("   "), "Введите название рецепта.");
  assert.equal(validateRecipeName("Каша"), null);
});

test("requires a selected product and positive amount", () => {
  assert.equal(
    validateRecipeComponentDraft({ ...validDraft, productId: "" }),
    "Выберите продукт.",
  );
  assert.equal(
    validateRecipeComponentDraft({ ...validDraft, amount: "0" }),
    "Количество должно быть больше нуля.",
  );
});

test("requires people count for package calculation", () => {
  assert.equal(
    validateRecipeComponentDraft({
      ...validDraft,
      calculationType: "package_per_people",
      peopleCount: "",
    }),
    "Укажите положительное число человек на упаковку.",
  );
});

test("normalizes component draft into API input", () => {
  assert.deepEqual(
    toRecipeComponentWriteInput({
      ...validDraft,
      amount: "120",
      unit: " gram ",
      calculationType: "package_per_people",
      peopleCount: "4",
    }),
    {
      product_id: "product-1",
      component_type: "base",
      amount: 120,
      unit: "gram",
      calculation_type: "package_per_people",
      people_count: 4,
    },
  );
});
