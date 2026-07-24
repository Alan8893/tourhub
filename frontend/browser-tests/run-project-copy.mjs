import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  CdpClient,
  findChromeExecutable,
  sleep,
  stopProcess,
  waitForExpression,
  waitForHttp,
} from "./club-settings-cdp.mjs";
import {
  removeChromeProfile,
  waitForPageTarget,
} from "./guided-release-browser-helpers.mjs";
import {
  projectCopyRequests,
  projectCopySource,
  projectCopySourceSnapshot,
  startProjectCopyApi,
} from "./project-copy-fixture.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5214;
const apiPort = 18119;
const debuggingPort = 9266;
const pageUrl = `http://127.0.0.1:${frontendPort}/browser-tests/project-copy.html?copyFrom=88`;
const profileDir = `/tmp/tourhub-project-copy-${process.pid}`;
const scenarioTimeoutMs = 75_000;

let activeApi;
let activeVite;
let activeChrome;
let activeClient;
let cleanupStarted = false;

async function cleanup() {
  if (cleanupStarted) return;
  cleanupStarted = true;
  activeClient?.close();
  activeClient = undefined;
  await Promise.allSettled([
    activeChrome ? stopProcess(activeChrome) : Promise.resolve(),
    activeVite ? stopProcess(activeVite) : Promise.resolve(),
  ]);
  if (activeApi) await Promise.race([activeApi.close(), sleep(2_000)]);
  await removeChromeProfile(profileDir, { allowResidual: true });
  await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
}

async function run() {
  await removeChromeProfile(profileDir);
  await mkdir(artifactDir, { recursive: true });
  activeApi = startProjectCopyApi(apiPort);
  await activeApi.listen();
  activeVite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      String(frontendPort),
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: `http://127.0.0.1:${apiPort}` },
      stdio: "ignore",
    },
  );
  await waitForHttp(pageUrl);
  activeChrome = spawn(
    findChromeExecutable(),
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      `--remote-debugging-port=${debuggingPort}`,
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp(`http://127.0.0.1:${debuggingPort}/json/version`);
    const target = await waitForPageTarget(debuggingPort, "/browser-tests/project-copy.html");
    activeClient = await CdpClient.connect(target.webSocketDebuggerUrl);
    await activeClient.send("Runtime.enable");
    await activeClient.send("Page.enable");
    await activeClient.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
    });

    await waitForExpression(
      activeClient,
      `document.body?.innerText?.includes("Копирование похода") &&
       document.body?.innerText?.includes("Кольский маршрут") &&
       [...document.querySelectorAll("button")].some((item) => item.textContent?.trim() === "Скопировать поход" && !item.disabled)`,
      "completed source copy form",
      20_000,
    );

    await activeClient.evaluate(`(() => {
      window.__projectCopyTest = {
        inputFor(text) {
          const label = [...document.querySelectorAll("label")]
            .find((item) => item.textContent?.trim().startsWith(text) && item.htmlFor);
          return label ? document.getElementById(label.htmlFor) : null;
        },
        setValue(text, value) {
          const input = this.inputFor(text);
          if (!input) throw new Error("Input not found: " + text);
          const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
          setter?.call(input, value);
          input.dispatchEvent(new Event("input", { bubbles: true }));
          input.dispatchEvent(new Event("change", { bubbles: true }));
        },
        choose(groupText, value) {
          const control = [...document.querySelectorAll(".MuiFormControl-root")]
            .find((item) => item.textContent?.includes(groupText));
          const input = control?.querySelector('input[type="radio"][value="' + value + '"]');
          if (!input) throw new Error("Radio not found: " + groupText + " / " + value);
          input.click();
        },
      };
    })()`);

    const defaults = await activeClient.evaluate(`({
      name: window.__projectCopyTest.inputFor("Название похода")?.value,
      participants: window.__projectCopyTest.inputFor("Количество участников")?.value,
      days: window.__projectCopyTest.inputFor("Количество дней")?.value,
      startDate: window.__projectCopyTest.inputFor("Дата начала похода")?.value,
    })`);
    assert.deepEqual(defaults, {
      name: "Кольский маршрут — копия",
      participants: "12",
      days: "5",
      startDate: "2026-08-01",
    });

    await activeClient.evaluate(`(() => {
      const helper = window.__projectCopyTest;
      helper.setValue("Название похода", "Кольский маршрут 2027");
      helper.setValue("Количество участников", "18");
      helper.setValue("Количество дней", "5");
      helper.setValue("Дата начала похода", "2027-08-10");
      helper.choose("Первый приём пищи", "breakfast");
      helper.choose("Последний приём пищи", "lunch");
      helper.choose("Какие рецепты использовать", "personal_preferred");
    })()`);
    await waitForExpression(
      activeClient,
      `window.__projectCopyTest.inputFor("Название похода")?.value === "Кольский маршрут 2027" &&
       window.__projectCopyTest.inputFor("Количество участников")?.value === "18"`,
      "editable destination parameters",
    );

    const submitted = await activeClient.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")]
        .find((item) => item.textContent?.trim() === "Скопировать поход" && !item.disabled);
      button?.click();
      return Boolean(button);
    })()`);
    assert.equal(submitted, true);
    await waitForExpression(
      activeClient,
      `[...document.querySelectorAll("button")].some((item) =>
        item.textContent?.trim() === "Копирование…" && item.disabled
      )`,
      "duplicate submission guard",
    );
    await activeClient.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")]
        .find((item) => item.textContent?.trim() === "Копирование…");
      button?.click();
    })()`);

    await waitForExpression(
      activeClient,
      `location.pathname === "/projects/501" &&
       document.body?.innerText?.includes("Новый проект #501") &&
       document.body?.innerText?.includes("Проект скопирован") &&
       document.body?.innerText?.includes("Скопировано слотов: 4, назначений: 7. Пропущено назначений: 1.") &&
       document.body?.innerText?.includes("Архивное блюдо")`,
      "copy success navigation and warning",
      20_000,
    );

    const copyRequests = projectCopyRequests.filter(
      (item) => item.method === "POST" && item.path === "/api/v1/projects/88/copy",
    );
    assert.equal(copyRequests.length, 1, "Copy endpoint must be called exactly once");
    assert.deepEqual(copyRequests[0].body, {
      name: "Кольский маршрут 2027",
      participants: 18,
      days: 5,
      start_date: "2027-08-10",
      first_meal: "breakfast",
      last_meal: "lunch",
      recipe_generation_mode: "personal_preferred",
    });
    assert.equal(JSON.stringify(projectCopySource), projectCopySourceSnapshot);
    assert.equal(
      projectCopyRequests.some(
        (item) => ["PATCH", "PUT", "DELETE"].includes(item.method) && item.path.includes("/projects/88"),
      ),
      false,
      "Source Project received a mutating request",
    );

    await activeClient.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(350);
    const layout = await activeClient.evaluate(`({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    })`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
      `Horizontal overflow at 360px: ${JSON.stringify(layout)}`,
    );
    const screenshot = await activeClient.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "project-copy-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    await writeFile(
      path.join(artifactDir, "project-copy.json"),
      JSON.stringify({ defaults, requests: projectCopyRequests, layout }, null, 2),
    );
    console.log("Project copy browser acceptance passed.");
  } catch (error) {
    await writeFile(
      path.join(artifactDir, "project-copy-error.txt"),
      `${error?.stack ?? error}\n`,
    );
    throw error;
  } finally {
    await cleanup();
  }
}

const watchdog = setTimeout(async () => {
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "project-copy-error.txt"),
    "Project copy browser acceptance timed out before completion.\n",
  );
  await cleanup();
  process.exit(1);
}, scenarioTimeoutMs);

run()
  .then(() => {
    clearTimeout(watchdog);
    process.exit(0);
  })
  .catch(async (error) => {
    clearTimeout(watchdog);
    console.error(error);
    await cleanup();
    process.exit(1);
  });
