import fsPromises from "node:fs/promises";
import { syncBuiltinESMExports } from "node:module";

const originalRm = fsPromises.rm.bind(fsPromises);
const chromeProfileSuffix = "tourhub-browser-acceptance-profile";
let profileRemovalCalls = 0;

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

fsPromises.rm = async (target, options) => {
  const isMealPlanChromeProfile = String(target).endsWith(chromeProfileSuffix);
  if (!isMealPlanChromeProfile) {
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

  // The first call prepares a clean browser profile and must succeed. The second
  // call is best-effort cleanup after Chrome has already been terminated.
  if (profileRemovalCalls > 1) return undefined;
  throw lastError;
};

syncBuiltinESMExports();
