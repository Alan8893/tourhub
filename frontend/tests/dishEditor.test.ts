import assert from "node:assert/strict";
import test from "node:test";

import { toDishWriteInput } from "../src/features/dish/model/dishEditor.ts";

test("normalizes dish form into API input", () => {
  assert.deepEqual(
    toDishWriteInput({ name: "  Каша с грибами  ", recipeId: "recipe-1" }),
    { name: "Каша с грибами", recipe_id: "recipe-1" },
  );
});

test("requires dish name", () => {
  assert.throws(
    () => toDishWriteInput({ name: "   ", recipeId: "recipe-1" }),
    /Введите название блюда/,
  );
});

test("requires active recipe selection", () => {
  assert.throws(
    () => toDishWriteInput({ name: "Каша", recipeId: "" }),
    /Выберите рецепт/,
  );
});
