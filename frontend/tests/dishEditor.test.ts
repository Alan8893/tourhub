import assert from "node:assert/strict";
import test from "node:test";

import {
  createMealRoleDraft,
  formatMealRoleSummary,
  setMealRoleMealTypeSelected,
  setMealRoleRepeatable,
  setMealRoleSelected,
  toDishMealRolesWriteInput,
  toDishWriteInput,
} from "../src/features/dish/model/dishEditor.ts";

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

test("creates meal role draft from persisted assignments", () => {
  const draft = createMealRoleDraft([
    {
      role: "addition",
      is_repeatable: true,
      allowed_meal_types: ["breakfast", "lunch", "dinner"],
    },
    {
      role: "snack",
      is_repeatable: false,
      allowed_meal_types: ["snack"],
    },
  ]);

  assert.deepEqual(draft.addition, {
    selected: true,
    isRepeatable: true,
    allowedMealTypes: {
      breakfast: true,
      snack: false,
      lunch: true,
      dinner: true,
    },
  });
  assert.deepEqual(draft.snack, {
    selected: true,
    isRepeatable: false,
    allowedMealTypes: {
      breakfast: false,
      snack: true,
      lunch: false,
      dinner: false,
    },
  });
});

test("serializes selected roles and meal types in stable domain order", () => {
  let draft = createMealRoleDraft([]);
  draft = setMealRoleSelected(draft, "drink", true);
  draft = setMealRoleMealTypeSelected(draft, "drink", "dinner", true);
  draft = setMealRoleMealTypeSelected(draft, "drink", "breakfast", true);
  draft = setMealRoleRepeatable(draft, "drink", true);
  draft = setMealRoleSelected(draft, "main", true);
  draft = setMealRoleMealTypeSelected(draft, "main", "lunch", true);

  assert.deepEqual(toDishMealRolesWriteInput(draft), {
    roles: [
      {
        role: "main",
        is_repeatable: false,
        allowed_meal_types: ["lunch"],
      },
      {
        role: "drink",
        is_repeatable: true,
        allowed_meal_types: ["breakfast", "dinner"],
      },
    ],
  });
});

test("requires explicit meal type compatibility for each selected role", () => {
  const draft = setMealRoleSelected(createMealRoleDraft([]), "main", true);
  assert.throws(
    () => toDishMealRolesWriteInput(draft),
    /Выберите хотя бы один приём пищи для роли «Основное блюдо»/,
  );
});

test("incompatible meal types cannot be selected", () => {
  let draft = setMealRoleSelected(createMealRoleDraft([]), "main", true);
  const unchanged = setMealRoleMealTypeSelected(draft, "main", "snack", true);
  assert.equal(unchanged, draft);

  draft = setMealRoleSelected(createMealRoleDraft([]), "snack", true);
  assert.equal(setMealRoleMealTypeSelected(draft, "snack", "breakfast", true), draft);
});

test("deselecting a role clears repeatability and meal types", () => {
  let draft = createMealRoleDraft([
    {
      role: "addition",
      is_repeatable: true,
      allowed_meal_types: ["breakfast", "lunch"],
    },
  ]);
  draft = setMealRoleSelected(draft, "addition", false);
  draft = setMealRoleSelected(draft, "addition", true);

  assert.deepEqual(draft.addition, {
    selected: true,
    isRepeatable: false,
    allowedMealTypes: {
      breakfast: false,
      snack: false,
      lunch: false,
      dinner: false,
    },
  });
});

test("repeatability and meal types cannot change for an unselected role", () => {
  const draft = createMealRoleDraft([]);
  assert.equal(setMealRoleRepeatable(draft, "snack", true), draft);
  assert.equal(setMealRoleMealTypeSelected(draft, "snack", "snack", true), draft);
});

test("formats visible catalogue classification with meal types", () => {
  assert.equal(formatMealRoleSummary([]), "Роли не назначены");
  assert.equal(
    formatMealRoleSummary([
      {
        role: "drink",
        is_repeatable: true,
        allowed_meal_types: ["breakfast", "lunch", "dinner"],
      },
      {
        role: "main",
        is_repeatable: false,
        allowed_meal_types: ["lunch", "dinner"],
      },
    ]),
    "Основное: обед, ужин; Напиток: завтрак, обед, ужин",
  );
});
