import assert from "node:assert/strict";
import test from "node:test";

import {
  formatDishGeneratorState,
  getDishGeneratorState,
} from "../src/features/dish/model/dishGeneratorReadiness.ts";

test("Dish without roles is explicitly not configured for the generator", () => {
  const state = getDishGeneratorState({ meal_roles: [] });

  assert.equal(state, "not_configured");
  assert.equal(formatDishGeneratorState(state), "Не настроено для генератора");
});

test("Dish with at least one explicit role is generator-ready", () => {
  const state = getDishGeneratorState({
    meal_roles: [
      {
        role: "main",
        is_repeatable: false,
        allowed_meal_types: ["dinner"],
      },
    ],
  });

  assert.equal(state, "ready");
  assert.equal(formatDishGeneratorState(state), "Готово для генератора");
});
