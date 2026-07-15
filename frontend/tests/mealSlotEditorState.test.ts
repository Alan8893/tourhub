import assert from "node:assert/strict";
import test from "node:test";

import {
  canSubmitDishSelection,
  createAddMealSlotDishCommand,
  createRemoveMealSlotDishCommand,
  createReplaceMealSlotDishCommand,
  formatDishCount,
  getMealSlotSuccessMessage,
  hasMealSlotMutationError,
  isMealSlotMutationBusy,
  mealSlotResponsiveDirection,
} from "../src/features/meal-slot/model/mealSlotEditorState.ts";

const idleState = {
  addPending: false,
  replacePending: false,
  removePending: false,
  addError: false,
  replaceError: false,
  removeError: false,
};

test("builds add, replace, and remove commands for MealSlot mutations", () => {
  assert.deepEqual(createAddMealSlotDishCommand("slot-1", " dish-2 "), {
    slotId: "slot-1",
    dishId: "dish-2",
  });
  assert.deepEqual(createReplaceMealSlotDishCommand("slot-1", "slot-dish-1", " dish-3 "), {
    slotId: "slot-1",
    slotDishId: "slot-dish-1",
    dishId: "dish-3",
  });
  assert.deepEqual(createRemoveMealSlotDishCommand("slot-1", "slot-dish-1"), {
    slotId: "slot-1",
    slotDishId: "slot-dish-1",
  });
});

test("blocks selection submission while any mutation is pending", () => {
  assert.equal(isMealSlotMutationBusy({ ...idleState, replacePending: true }), true);
  assert.equal(canSubmitDishSelection("dish-2", true), false);
  assert.equal(canSubmitDishSelection("   ", false), false);
  assert.equal(canSubmitDishSelection("dish-2", false), true);
});

test("reports mutation errors from add, replace, or remove operations", () => {
  assert.equal(hasMealSlotMutationError(idleState), false);
  assert.equal(hasMealSlotMutationError({ ...idleState, addError: true }), true);
  assert.equal(hasMealSlotMutationError({ ...idleState, replaceError: true }), true);
  assert.equal(hasMealSlotMutationError({ ...idleState, removeError: true }), true);
});

test("returns Russian success feedback for every mutation", () => {
  assert.equal(getMealSlotSuccessMessage("add"), "Блюдо добавлено.");
  assert.equal(getMealSlotSuccessMessage("replace"), "Блюдо заменено.");
  assert.equal(getMealSlotSuccessMessage("remove"), "Блюдо удалено.");
});

test("formats dish counts with Russian plural forms", () => {
  assert.equal(formatDishCount(0), "0 блюд");
  assert.equal(formatDishCount(1), "1 блюдо");
  assert.equal(formatDishCount(2), "2 блюда");
  assert.equal(formatDishCount(5), "5 блюд");
  assert.equal(formatDishCount(11), "11 блюд");
  assert.equal(formatDishCount(21), "21 блюдо");
  assert.equal(formatDishCount(24), "24 блюда");
  assert.equal(formatDishCount(25), "25 блюд");
});

test("uses a stacked layout on mobile and an inline layout from the small breakpoint", () => {
  assert.deepEqual(mealSlotResponsiveDirection, {
    xs: "column",
    sm: "row",
  });
});
