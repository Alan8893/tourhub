import assert from "node:assert/strict";
import test from "node:test";

import {
  getAuditExportFilename,
  toAuditIsoTimestamp,
} from "../src/features/audit/model/auditExport.ts";

test("normalizes audit date filters to ISO timestamps", () => {
  assert.equal(
    toAuditIsoTimestamp("2026-07-22T10:15:00Z"),
    "2026-07-22T10:15:00.000Z",
  );
  assert.equal(toAuditIsoTimestamp(""), undefined);
  assert.equal(toAuditIsoTimestamp("not-a-date"), undefined);
});

test("uses the Backend audit export filename safely", () => {
  assert.equal(
    getAuditExportFilename('attachment; filename="tourhub-audit.csv"'),
    "tourhub-audit.csv",
  );
  assert.equal(
    getAuditExportFilename("attachment; filename*=UTF-8''audit-%D0%B6%D1%83%D1%80%D0%BD%D0%B0%D0%BB.csv"),
    "audit-журнал.csv",
  );
  assert.equal(getAuditExportFilename(), "tourhub-audit.csv");
});
