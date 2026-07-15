import assert from "node:assert/strict";
import test from "node:test";

import type { DishCatalogueReadiness } from "../src/features/dish/api/dishApi.ts";
import {
  formatClassificationSummary,
  formatCoverageGap,
  formatRecommendationGap,
  getMissingRecommendedCoverage,
  getMissingRequiredCoverage,
} from "../src/features/dish/model/dishCatalogueReadiness.ts";

const readiness: DishCatalogueReadiness = {
  ready: false,
  active_dish_count: 3,
  classified_dish_count: 2,
  unclassified_dish_count: 1,
  coverage: [
    {
      meal_type: "breakfast",
      role: "main",
      required: true,
      candidate_count: 0,
      minimum_required: 1,
      ready: false,
    },
    {
      meal_type: "breakfast",
      role: "drink",
      required: false,
      candidate_count: 0,
      minimum_required: 1,
      ready: false,
    },
    {
      meal_type: "lunch",
      role: "main",
      required: true,
      candidate_count: 1,
      minimum_required: 1,
      ready: true,
    },
  ],
};

test("separates blocking and recommended catalogue gaps", () => {
  assert.deepEqual(getMissingRequiredCoverage(readiness), [readiness.coverage[0]]);
  assert.deepEqual(getMissingRecommendedCoverage(readiness), [readiness.coverage[1]]);
});

test("formats Russian catalogue readiness messages", () => {
  assert.equal(
    formatCoverageGap(readiness.coverage[0]),
    "Завтрак: нужно добавить основное блюдо.",
  );
  assert.equal(
    formatRecommendationGap(readiness.coverage[1]),
    "Завтрак: желательно добавить напиток.",
  );
  assert.equal(
    formatClassificationSummary(readiness),
    "Без ролей осталось блюд: 1 из 3.",
  );
});

test("formats empty and fully classified catalogues", () => {
  assert.equal(
    formatClassificationSummary({
      ...readiness,
      active_dish_count: 0,
      classified_dish_count: 0,
      unclassified_dish_count: 0,
    }),
    "В каталоге нет активных блюд.",
  );
  assert.equal(
    formatClassificationSummary({
      ...readiness,
      ready: true,
      classified_dish_count: 3,
      unclassified_dish_count: 0,
    }),
    "Все активные блюда классифицированы: 3.",
  );
});
