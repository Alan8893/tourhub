import { spawn } from "node:child_process";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cleanupImport = "./browser-tests/retry-chrome-profile-cleanup.mjs";
const successPattern = /passed\./i;
const scenarioTimeoutMs = 90_000;
const teardownGraceMs = 6_000;

const scenarios = [
  { script: "browser-tests/run-meal-plan-editor.mjs", cleanup: true },
  { script: "browser-tests/run-dish-meal-role-editor.mjs" },
  { script: "browser-tests/run-dish-catalogue-readiness.mjs", attempts: 2 },
  { script: "browser-tests/run-app-layout-mobile.mjs", attempts: 2 },
  { script: "browser-tests/run-purchase-checklist.mjs", cleanup: true, attempts: 2 },
  {
    script: "browser-tests/run-purchase-responsible-person.mjs",
    cleanup: true,
    attempts: 2,
  },
  { script: "browser-tests/run-equipment-list-with-retry.mjs" },
  { script: "browser-tests/run-documents.mjs", cleanup: true },
  { script: "browser-tests/run-consolidated-documents.mjs", cleanup: true },
  { script: "browser-tests/run-club-settings.mjs", cleanup: true },
  { script: "browser-tests/run-appearance-settings.mjs", cleanup: true },
  { script: "browser-tests/run-document-appearance-settings.mjs", cleanup: true },
  { script: "browser-tests/run-module-settings.mjs", cleanup: true },
  { script: "browser-tests/run-invitation-settings.mjs", cleanup: true },
  { script: "browser-tests/run-mail-settings.mjs", cleanup: true },
  { script: "browser-tests/run-account-admin.mjs", cleanup: true },
  { script: "browser-tests/run-access-auth.mjs", cleanup: true },
  { script: "browser-tests/run-account-profile.mjs", cleanup: true },
  { script: "browser-tests/run-project-team-access.mjs", cleanup: true },
  { script: "browser-tests/run-recipe-moderation.mjs", cleanup: true },
  { script: "browser-tests/run-audit-log.mjs", cleanup: true },
  { script: "browser-tests/run-audit-export.mjs", cleanup: true },
  { script: "browser-tests/run-product-archive.mjs", cleanup: true, attempts: 2 },
  { script: "browser-tests/run-dish-archive.mjs", cleanup: true, attempts: 2 },
  { script: "browser-tests/run-guided-release.mjs", cleanup: true },
];

function stopProcessGroup(child) {
  if (!child.pid) return;
  try {
    process.kill(-child.pid, "SIGKILL");
  } catch (error) {
    if (error?.code !== "ESRCH") throw error;
  }
}

function runAttempt(scenario, attempt) {
  return new Promise((resolve) => {
    const args = scenario.cleanup
      ? ["--import", cleanupImport, scenario.script]
      : [scenario.script];
    const child = spawn(process.execPath, args, {
      cwd: frontendRoot,
      detached: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let settled = false;
    let successMarkerSeen = false;
    let teardownTimer;
    let timeoutTimer;

    const finish = (result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeoutTimer);
      clearTimeout(teardownTimer);
      resolve(result);
    };

    const handleOutput = (stream, chunk) => {
      stream.write(chunk);
      if (successMarkerSeen || !successPattern.test(String(chunk))) return;
      successMarkerSeen = true;
      teardownTimer = setTimeout(() => {
        stopProcessGroup(child);
        finish({ ok: true, forcedAfterSuccess: true });
      }, teardownGraceMs);
    };

    child.stdout.on("data", (chunk) => handleOutput(process.stdout, chunk));
    child.stderr.on("data", (chunk) => handleOutput(process.stderr, chunk));

    child.on("error", (error) => finish({ ok: false, error }));
    child.on("exit", (code, signal) => {
      if (successMarkerSeen || code === 0) {
        finish({ ok: true, code, signal });
        return;
      }
      finish({
        ok: false,
        error: new Error(
          `${scenario.script} attempt ${attempt} exited with code ${code} signal ${signal}`,
        ),
      });
    });

    timeoutTimer = setTimeout(() => {
      stopProcessGroup(child);
      finish({
        ok: false,
        error: new Error(
          `${scenario.script} attempt ${attempt} timed out before a success marker`,
        ),
      });
    }, scenarioTimeoutMs);
  });
}

async function runScenario(scenario) {
  const attempts = scenario.attempts ?? 1;
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    console.log(`\n=== ${scenario.script} (${attempt}/${attempts}) ===`);
    const result = await runAttempt(scenario, attempt);
    if (result.ok) {
      if (result.forcedAfterSuccess) {
        console.log(`${scenario.script}: teardown process group stopped after success marker.`);
      }
      return;
    }
    console.error(result.error);
    if (attempt === attempts) throw result.error;
    console.log(`${scenario.script}: retrying after failed attempt.`);
  }
}

for (const scenario of scenarios) {
  await runScenario(scenario);
}

console.log("All frontend browser acceptance scenarios passed.");
