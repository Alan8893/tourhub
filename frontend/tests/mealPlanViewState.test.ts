import assert from "node:assert/strict";
import test from "node:test";

import {
  countMealPlanDayDishes,
  getMealPlanViewState,
  isMealPlanDayExpandedByDefault,
  sortMealSlots,
} from "../src/features/meal-plan/model/mealPlanViewState.ts";

test("returns loading while the meal plan request is pending", () => {
  assert.equal(
    getMealPlanViewState({ isLoading: true, isError: false, hasMealPlan: false }),
    "loading",
  );
});

test("returns error when the meal plan request fails", () => {
  assert.equal(
    getMealPlanViewState({ isLoading: false, isError: true, hasMealPlan: false }),
    "error",
  );
});

test("returns empty when a project has no generated meal plan", () => {
  assert.equal(
    getMealPlanViewState({ isLoading: false, isError: false, hasMealPlan: false }),
    "empty",
  );
});

test("returns ready when meal plan data is available", () => {
  assert.equal(
    getMealPlanViewState({ isLoading: false, isError: false, hasMealPlan: true }),
    "ready",
  );
});

test("sorts meal slots by the trip meal sequence", () => {
  const sorted = sortMealSlots([
    { meal_type: "dinner", dishes: [] },
    { meal_type: "breakfast", dishes: [] },
    { meal_type: "lunch", dishes: [] },
    { meal_type: "snack", dishes: [] },
  ]);

  assert.deepEqual(
    sorted.map((slot) => slot.meal_type),
    ["breakfast", "snack", "lunch", "dinner"],
  );
});

test("counts dishes for a collapsible day summary", () => {
  assert.equal(
    countMealPlanDayDishes([
      { meal_type: "breakfast", dishes: [{ id: "1" }] },
      { meal_type: "dinner", dishes: [{ id: "2" }, { id: "3" }] },
    ]),
    3,
  );
});

test("expands only the first day by default", () => {
  assert.equal(isMealPlanDayExpandedByDefault(0), true);
  assert.equal(isMealPlanDayExpandedByDefault(1), false);
});
