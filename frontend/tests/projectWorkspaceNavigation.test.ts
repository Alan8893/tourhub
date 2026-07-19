import assert from "node:assert/strict";
import test from "node:test";

import {
  buildProjectWorkspacePath,
  normalizeProjectWorkspaceSection,
  PROJECT_WORKSPACE_SECTIONS,
} from "../src/features/project-workspace/model/projectWorkspaceNavigation.ts";

test("exposes the approved workspace sections in navigation order", () => {
  assert.deepEqual(
    PROJECT_WORKSPACE_SECTIONS.map((section) => section.id),
    ["overview", "menu", "shopping", "equipment", "documents"],
  );
});

test("normalizes missing and unsupported sections to overview", () => {
  assert.equal(normalizeProjectWorkspaceSection(undefined), "overview");
  assert.equal(normalizeProjectWorkspaceSection("unknown"), "overview");
});

test("keeps supported project workspace sections", () => {
  assert.equal(normalizeProjectWorkspaceSection("shopping"), "shopping");
  assert.equal(normalizeProjectWorkspaceSection("documents"), "documents");
});

test("builds a compact overview URL and explicit section URLs", () => {
  assert.equal(buildProjectWorkspacePath(77, "overview"), "/projects/77");
  assert.equal(buildProjectWorkspacePath(77, "menu"), "/projects/77/menu");
  assert.equal(
    buildProjectWorkspacePath(77, "equipment"),
    "/projects/77/equipment",
  );
});
