import assert from "node:assert/strict";
import test from "node:test";

import { normalizeApiUrl } from "../src/shared/config/apiUrl.ts";

test("uses the same-origin API proxy when no URL is configured", () => {
  assert.equal(normalizeApiUrl(), "/api/v1");
  assert.equal(normalizeApiUrl("   "), "/api/v1");
});

test("normalizes API version paths through the same-origin proxy", () => {
  assert.equal(normalizeApiUrl("/v1"), "/api/v1");
  assert.equal(normalizeApiUrl("/v1/projects"), "/api/v1/projects");
});

test("preserves an explicitly configured remote API origin", () => {
  assert.equal(
    normalizeApiUrl("http://192.168.88.33:8000/api/v1/"),
    "http://192.168.88.33:8000/api/v1",
  );
});
