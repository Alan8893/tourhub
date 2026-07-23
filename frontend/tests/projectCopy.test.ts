import assert from "node:assert/strict";
import test from "node:test";

import type { Project, ProjectCopyResponse } from "../src/features/project/api/projectApi.ts";
import {
  buildProjectCopyDefaults,
  projectCopySummary,
} from "../src/features/project/model/projectCopy.ts";

function project(overrides: Partial<Project> = {}): Project {
  return {
    id: 10,
    name: "Кольский маршрут",
    participants: 12,
    days: 5,
    start_date: "2026-08-01",
    first_meal: "dinner",
    last_meal: "lunch",
    recipe_generation_mode: "club_and_personal",
    status: "completed",
    owner_user_id: 1,
    owner_display_name: "Owner",
    capabilities: {
      can_view: true,
      can_manage_project: false,
      can_manage_team: false,
      can_transfer_ownership: false,
      can_edit_menu: false,
      can_operate_shopping: false,
      can_operate_equipment: false,
      can_generate_documents: true,
      can_delete: true,
    },
    ...overrides,
  };
}

test("builds editable destination defaults from a completed project", () => {
  assert.deepEqual(buildProjectCopyDefaults(project()), {
    name: "Кольский маршрут — копия",
    participants: 12,
    days: 5,
    start_date: "2026-08-01",
    first_meal: "dinner",
    last_meal: "lunch",
    recipe_generation_mode: "club_and_personal",
  });
});

test("omits nullable optional fields from copy defaults", () => {
  assert.deepEqual(buildProjectCopyDefaults(project({ start_date: null, first_meal: null, last_meal: null })), {
    name: "Кольский маршрут — копия",
    participants: 12,
    days: 5,
    start_date: undefined,
    first_meal: undefined,
    last_meal: undefined,
    recipe_generation_mode: "club_and_personal",
  });
});

test("summarizes copied and skipped assignments", () => {
  const result: ProjectCopyResponse = {
    project_id: 22,
    meal_plan_id: "mp-22",
    copied_slot_count: 3,
    copied_assignment_count: 7,
    skipped_assignment_count: 2,
    warnings: ["one", "two"],
  };
  assert.equal(
    projectCopySummary(result),
    "Скопировано слотов: 3, назначений: 7. Пропущено назначений: 2.",
  );
});
