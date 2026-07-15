import assert from "node:assert/strict";
import test from "node:test";

import { extractDishOptions } from "../src/features/meal-slot/model/dishOptions.ts";

test("extracts dish options from the backend list envelope", () => {
  assert.deepEqual(
    extractDishOptions({
      items: [
        { id: "dish-1", name: "Плов" },
        { id: "dish-2", name: "Суп" },
      ],
    }),
    [
      { id: "dish-1", name: "Плов" },
      { id: "dish-2", name: "Суп" },
    ],
  );
});
