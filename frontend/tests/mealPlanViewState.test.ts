import assert from "node:assert/strict";
import test from "node:test";

import { getMealPlanViewState } from "../src/features/meal-plan/model/mealPlanViewState.ts";

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
