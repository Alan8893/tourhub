import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  catalogImportOwnershipRequests,
  startCatalogImportOwnershipApi,
} from "./catalog-import-ownership-fixture.mjs";
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
  selectMuiOption,
  setFieldByLabel,
} from "./invitation-settings-actions.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5215/browser-tests/catalog-import-ownership.html";
const chromeDebugUrl = "http://127.0.0.1:9267";
const profileDir = `/tmp/tourhub-catalog-import-ownership-${process.pid}`;
const scenarioTimeoutMs = 90_000;
const recipesCsv = `recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority
Походная гречка;Гречка;base;80;gram;per_person;;cooking_tip;Промыть крупу;10
`;

async function waitForRequest(pathname, count, description) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const matches = catalogImportOwnershipRequests.filter(
      (item) => item.path === pathname,
    );
    if (matches.length >= count) return matches[count - 1];
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function run() {
  await rm(profileDir, {
    recursive: true,
    force: true,
    maxRetries: 10,
    retryDelay: 100,
  });
  await mkdir(artifactDir, { recursive: true });
  const api = startCatalogImportOwnershipApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5215",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18118" },
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
      "--remote-debugging-port=9267",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );
  let client;

  try {
    await waitForHttp(`${chromeDebugUrl}/json/version`);
    const targets = await fetch(`${chromeDebugUrl}/json/list`).then((response) =>
      response.json(),
    );
    const target = targets.find((item) =>
      item.url.includes("catalog-import-ownership.html"),
    );
    assert.ok(target?.webSocketDebuggerUrl);
    client = await CdpClient.connect(target.webSocketDebuggerUrl);
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
      `document.body?.innerText?.includes("Массовый импорт") &&
       document.body?.innerText?.includes("Продукты")`,
      "loaded catalog import page",
    );
    await selectMuiOption(
      client,
      "Тип данных",
      "Рецепты, компоненты и заметки",
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Область владения") &&
       document.body?.innerText?.includes("Клубные рецепты")`,
      "ownership selector",
    );
    await selectMuiOption(client, "Область владения", "Личные рецепты");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("личные черновики")`,
      "personal ownership explanation",
    );
    assert.equal(
      await setFieldByLabel(client, "Содержимое CSV", recipesCsv),
      true,
    );
    assert.equal(await clickButton(client, "Проверить файл"), true);

    const previewRequest = await waitForRequest(
      "/api/v1/catalog-import/preview",
      1,
      "personal Recipe preview request",
    );
    assert.equal(previewRequest.body.kind, "recipes");
    assert.equal(previewRequest.body.ownership_scope, "personal");
    assert.equal(previewRequest.body.preview_token, undefined);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Личные рецепты") &&
       document.body?.innerText?.includes("Файл прошёл проверку") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Импортировать" && !item.disabled,
       )`,
      "personal Recipe preview",
    );

    assert.equal(await clickButton(client, "Импортировать"), true);
    const applyRequest = await waitForRequest(
      "/api/v1/catalog-import/apply",
      1,
      "personal Recipe apply request",
    );
    assert.equal(applyRequest.body.kind, "recipes");
    assert.equal(applyRequest.body.ownership_scope, "personal");
    assert.equal(applyRequest.body.preview_token, api.previewToken);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("создано личных черновиков 1")`,
      "personal Recipe import success",
    );

    await selectMuiOption(client, "Область владения", "Клубные рецепты");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("статусом опубликованных") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Импортировать" && item.disabled,
       ) &&
       !document.body?.innerText?.includes("Файл прошёл проверку")`,
      "preview invalidated after ownership change",
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(350);
    const layout = await client.evaluate(`({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    })`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
      `Horizontal overflow: ${JSON.stringify(layout)}`,
    );

    await writeFile(
      path.join(artifactDir, "catalog-import-ownership.json"),
      JSON.stringify({ requests: catalogImportOwnershipRequests, layout }, null, 2),
    );
    client.close();
    client = undefined;
    console.log("Ownership-aware catalog import browser acceptance passed.");
  } catch (error) {
    const page = client
      ? await client.evaluate(`({
          bodyText: document.body?.innerText ?? "",
          bodyHtml: document.body?.innerHTML?.slice(0, 30000) ?? "",
        })`)
      : null;
    await writeFile(
      path.join(artifactDir, "catalog-import-ownership-error.json"),
      JSON.stringify(
        {
          error: error?.stack ?? String(error),
          page,
          requests: catalogImportOwnershipRequests,
        },
        null,
        2,
      ),
    );
    throw error;
  } finally {
    client?.close();
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await Promise.race([api.close(), sleep(2_000)]);
    await rm(profileDir, {
      recursive: true,
      force: true,
      maxRetries: 10,
      retryDelay: 100,
    });
  }
}

const watchdog = setTimeout(() => {
  console.error("Ownership-aware catalog import browser acceptance timed out.");
  process.exit(1);
}, scenarioTimeoutMs);

run()
  .then(() => {
    clearTimeout(watchdog);
    process.exit(0);
  })
  .catch((error) => {
    clearTimeout(watchdog);
    console.error(error);
    process.exit(1);
  });
