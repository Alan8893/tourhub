import childProcess from "node:child_process";
import fsPromises from "node:fs/promises";
import { syncBuiltinESMExports } from "node:module";

const originalRm = fsPromises.rm.bind(fsPromises);
const originalSpawn = childProcess.spawn.bind(childProcess);
const chromeProfileSuffixes = [
  "tourhub-browser-acceptance-profile",
  "tourhub-purchase-checklist-profile",
  "tourhub-equipment-list-profile",
  "tourhub-documents-profile",
  "tourhub-club-settings-profile",
];
let profileRemovalCalls = 0;

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

fsPromises.rm = async (target, options) => {
  const isAcceptanceChromeProfile = chromeProfileSuffixes.some((suffix) =>
    String(target).endsWith(suffix),
  );
  if (!isAcceptanceChromeProfile) {
    return originalRm(target, options);
  }

  profileRemovalCalls += 1;
  let lastError;
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      return await originalRm(target, options);
    } catch (error) {
      if (error?.code !== "ENOTEMPTY") throw error;
      lastError = error;
      await sleep(50);
    }
  }

  if (profileRemovalCalls > 1) return undefined;
  throw lastError;
};

childProcess.spawn = (command, args, options) => {
  const nextArgs = Array.isArray(args) ? [...args] : args;
  if (
    Array.isArray(nextArgs) &&
    nextArgs.includes("--remote-debugging-port=9232") &&
    nextArgs.at(-1) === "about:blank"
  ) {
    nextArgs[nextArgs.length - 1] =
      "http://127.0.0.1:5180/browser-tests/documents.html";
  }
  return originalSpawn(command, nextArgs, options);
};

syncBuiltinESMExports();
