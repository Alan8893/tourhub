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
  clickButton,
  setInput,
  setNumberInput,
  waitForRequest,
} from "./guided-release-browser-helpers.mjs";
import { createGuidedReleaseMockApi } from "./guided-release-mock-api.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5182;
const apiPort = 18084;
const debuggingPort = 9234;
const pageUrl = `http://127.0.0.1:${frontendPort}/projects/new`;
const profileDir = "/tmp/tourhub-guided-release-profile";

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const mockApi = createGuidedReleaseMockApi(apiPort);
  await mockApi.listen();

  const vite = spawn(
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

  const chrome = spawn(
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
    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then(
      (response) => response.json(),
    );
    const target = targets.find((item) => item.type === "page");
    assert.ok(target?.webSocketDebuggerUrl);
    const client = await CdpClient.connect(target.webSocketDebuggerUrl);
    await client.send("Runtime.enable");
    await client.send("Page.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
    });

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Создание похода")`,
      "project creation page",
    );
    await setInput(
      client,
      'input[placeholder="Например: Карелия 2026"]',
      "Карелия 2026",
    );
    await setNumberInput(client, 0, "8");
    await setNumberInput(client, 1, "3");
    await clickButton(client, "Создать поход");

    await waitForExpression(
      client,
      `location.pathname === "/projects/77" &&
       document.body?.innerText?.includes("Сформируйте меню для этого похода")`,
      "new project workspace",
    );
    const initialText = await client.evaluate("document.body.innerText");
    assert.ok(!initialText.includes("Не удалось загрузить список закупки"));

    const createRequests = await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/projects",
    );
    assert.deepEqual(createRequests[0].body, {
      name: "Карелия 2026",
      participants: 8,
      days: 3,
      first_meal: "dinner",
      last_meal: "dinner",
    });

    await clickButton(client, "Сформировать меню");
    await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/meal-plans/project/77/generate",
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Рассчитайте закупку, создайте чек-лист и список оборудования")`,
      "preparation action",
    );

    await clickButton(client, "Подготовить проект");
    await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/projects/77/prepare",
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Проект подготовлен") &&
       document.body.innerText.includes("✓ Оборудование") &&
       document.body.innerText.includes("✓ Документы готовы") &&
       document.body.innerText.includes("Русские документы закупки и оборудования готовы")`,
      "complete guided project",
    );

    await client.send("Page.reload", { ignoreCache: true });
    await waitForExpression(
      client,
      `location.pathname === "/projects/77" &&
       document.body?.innerText?.includes("Проект подготовлен") &&
       document.body.innerText.includes("✓ Оборудование") &&
       document.body.innerText.includes("Скачать полный пакет")`,
      "restored prepared project",
      20_000,
    );
    assert.equal(
      mockApi.requests.filter(
        (request) =>
          request.method === "POST" &&
          request.path === "/api/v1/projects/77/prepare",
      ).length,
      1,
      "Reload must not prepare the project again",
    );

    await clickButton(client, "Скачать полный пакет");
    await waitForRequest(
      mockApi.requests,
      "GET",
      "/api/v1/projects/77/documents/package",
    );
    await waitForRequest(
      mockApi.requests,
      "GET",
      "/api/v1/projects/77/preparation",
      2,
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(250);
    const layout = await client.evaluate(`(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    }))()`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
      `Horizontal overflow at 360px: ${JSON.stringify(layout)}`,
    );

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "guided-release-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Guided release browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await mockApi.close();
    await rm(profileDir, { recursive: true, force: true });
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "guided-release-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
