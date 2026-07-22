import assert from "node:assert/strict";
import test from "node:test";

import type { ArchivedDish } from "../src/features/dish/api/dishArchiveApi.ts";
import {
  canRestoreArchivedDish,
  dishArchiveNotice,
} from "../src/features/dish/model/dishArchive.ts";

function dish(overrides: Partial<ArchivedDish> = {}): ArchivedDish {
  return {
    id: "dish-1",
    name: "Гречневая каша",
    recipe_name: "Каша базовая",
    is_archived: true,
    archived_by_alcohol_policy: false,
    ...overrides,
  };
}

test("allows restore only for manually archived dishes", () => {
  assert.equal(canRestoreArchivedDish(dish()), true);
  assert.equal(
    canRestoreArchivedDish(dish({ archived_by_alcohol_policy: true })),
    false,
  );
  assert.equal(canRestoreArchivedDish(dish({ is_archived: false })), false);
});

test("explains central policy lock without exposing internal data", () => {
  assert.equal(dishArchiveNotice(dish()), null);
  const notice = dishArchiveNotice(dish({ archived_by_alcohol_policy: true }));
  assert.ok(notice?.includes("алкогольными"));
  assert.equal(notice?.toLowerCase().includes("token"), false);
  assert.equal(notice?.toLowerCase().includes("cookie"), false);
});
