import assert from "node:assert/strict";
import test from "node:test";

import { getRecipeLibraryViewState } from "../src/features/recipe/model/recipeLibraryViewState.ts";

test("returns loading while recipes are requested", () => {
  assert.equal(
    getRecipeLibraryViewState({ isLoading: true, isError: false, recipeCount: 0 }),
    "loading",
  );
});

test("returns error when the recipe request fails", () => {
  assert.equal(
    getRecipeLibraryViewState({ isLoading: false, isError: true, recipeCount: 0 }),
    "error",
  );
});

test("returns empty for an empty recipe library", () => {
  assert.equal(
    getRecipeLibraryViewState({ isLoading: false, isError: false, recipeCount: 0 }),
    "empty",
  );
});

test("returns ready when recipes are available", () => {
  assert.equal(
    getRecipeLibraryViewState({ isLoading: false, isError: false, recipeCount: 2 }),
    "ready",
  );
});
