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

    const defaults = await activeClient.evaluate(`(() => {
      const inputFor = (text) => {
        const label = [...document.querySelectorAll("label")]
          .find((item) => item.textContent?.trim() === text && item.htmlFor);
        return label ? document.getElementById(label.htmlFor) : null;
      };
      return {
        name: inputFor("Название похода")?.value,
        participants: inputFor("Количество участников")?.value,
        days: inputFor("Количество дней")?.value,
        startDate: inputFor("Дата начала похода")?.value,
      };
    })()`);
    assert.deepEqual(defaults, {
      name: "Кольский маршрут — копия",
      participants: "12",
      days: "5",
      startDate: "2026-08-01",
    });

    const edited = await activeClient.evaluate(`(() => {
      const inputFor = (text) => {
        const label = [...document.querySelectorAll("label")]
          .find((item) => item.textContent?.trim() === text && item.htmlFor);
        return label ? document.getElementById(label.htmlFor) : null;
      };
      const setValue = (input, value) => {
        if (!input) throw new Error("Input not found");
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
        setter?.call(input, value);
        input.dispatchEvent(new Event("input", { bubbles: true }));
        input.dispatchEvent(new Event("change", { bubbles: true }));
      };
      const choose = (groupText, value) => {
        const control = [...document.querySelectorAll(".MuiFormControl-root")]
          .find((item) => item.textContent?.includes(groupText));
        const input = control?.querySelector('input[type="radio"][value="' + value + '"]');
        if (!input) throw new Error("Radio not found: " + groupText + " / " + value);
        input.click();
      };
      setValue(inputFor("Название похода"), "Кольский маршрут 2027");
      setValue(inputFor("Количество участников"), "18");
      setValue(inputFor("Количество дней"), "5");
      setValue(inputFor("Дата начала похода"), "2027-08-10");
      choose("Первый приём пищи", "breakfast");
      choose("Последний приём пищи", "lunch");
      choose("Какие рецепты использовать", "personal_preferred");
      return true;
    })()`);
    assert.equal(edited, true);

    await waitForExpression(
      activeClient,
      `(() => {
        const label = [...document.querySelectorAll("label")]
          .find((item) => item.textContent?.trim() === "Название похода" && item.htmlFor);
        return label && document.getElementById(label.htmlFor)?.value === "Кольский маршрут 2027";
      })()`,
      "editable destination parameters",
    );

    const submitted = await activeClient.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")]
        .find((item) => item.textContent?.trim() === "Скопировать поход" && !item.disabled);
      if (!button) return false;
      button.click();
      return true;
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
    assert.equal(
      JSON.stringify(projectCopySource),
      projectCopySourceSnapshot,
      "Completed source fixture changed during copy",
    );
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
