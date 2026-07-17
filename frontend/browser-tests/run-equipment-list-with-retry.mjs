import { spawn } from "node:child_process";
import { readFile, rm } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const runner = path.join(frontendRoot, "browser-tests", "run-equipment-list.mjs");
const cleanupHook = path.join(
  frontendRoot,
  "browser-tests",
  "retry-chrome-profile-cleanup.mjs",
);
const errorFile = path.join(
  frontendRoot,
  "browser-test-artifacts",
  "equipment-list-error.txt",
);
const maximumAttempts = 3;
const transientPatterns = [
  /Browser evaluation failed/i,
  /\bUncaught\b/i,
  /Target closed/i,
];

const sleep = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

function runAttempt() {
  return new Promise((resolve) => {
    const child = spawn(
      process.execPath,
      ["--import", cleanupHook, runner],
      {
        cwd: frontendRoot,
        stdio: "inherit",
      },
    );

    child.once("error", () => resolve(1));
    child.once("close", (code) => resolve(code ?? 1));
  });
}

async function readFailure() {
  try {
    return await readFile(errorFile, "utf8");
  } catch {
    return "";
  }
}

for (let attempt = 1; attempt <= maximumAttempts; attempt += 1) {
  await rm(errorFile, { force: true });
  const exitCode = await runAttempt();
  if (exitCode === 0) process.exit(0);

  const failure = await readFailure();
  const isTransient = transientPatterns.some((pattern) => pattern.test(failure));
  if (!isTransient || attempt === maximumAttempts) {
    process.exit(exitCode);
  }

  console.warn(
    `Transient equipment browser CDP failure; retrying (${attempt}/${maximumAttempts}).`,
  );
  await sleep(400 * attempt);
}
