import assert from "node:assert/strict";
import test from "node:test";

import type { AccountSession } from "../src/features/account/api/accountApi.ts";
import {
  canRevokeAccountSession,
  formatAccountSessionTime,
  withoutAccountSession,
} from "../src/features/account/model/accountSessions.ts";

const sessions: AccountSession[] = [
  {
    id: 101,
    created_at: "2026-07-22T08:00:00Z",
    last_seen_at: "2026-07-22T10:00:00Z",
    expires_at: "2026-08-21T08:00:00Z",
    is_current: true,
  },
  {
    id: 202,
    created_at: "2026-07-20T07:30:00Z",
    last_seen_at: "2026-07-21T18:45:00Z",
    expires_at: "2026-08-19T07:30:00Z",
    is_current: false,
  },
];

test("allows individual revocation only for another session", () => {
  assert.equal(canRevokeAccountSession(sessions[0]), false);
  assert.equal(canRevokeAccountSession(sessions[1]), true);
});

test("removes only the successfully revoked session", () => {
  assert.deepEqual(withoutAccountSession(sessions, 202), [sessions[0]]);
  assert.deepEqual(withoutAccountSession(sessions, 999), sessions);
});

test("formats session timestamps for Russian account UI", () => {
  const formatted = formatAccountSessionTime("2026-07-22T10:00:00Z");
  assert.ok(formatted.includes("2026"));
  assert.ok(formatted.length > 8);
});
