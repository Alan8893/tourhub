import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  productArchiveRequests,
  startProductArchiveApi,
} from "./product-archive-fixture.mjs";
import {
  CdpClient,
  findChromeExecutable,
  sleep,
  stopProcess,
  waitForExpression,
  waitForHttp,
} from "./club-settings-cdp.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5213/browser-tests/product-archive.html";
const profileDir = `/tmp/tourhub-product-archive-${process.pid}`;
const scenarioTimeoutMs = 90_000;

let activeApi;
let activeVite;
let activeChrome;
let activeClient;
let cleanupStarted = false;

async function clickTextButton(client, text) {
  return client.evaluate(`(() => {
    const text = ${JSON.stringify(text)};
    const button = [...document.querySelectorAll("button")]
      .find((item) => item.textContent?.trim() === text && !item.disabled);
    if (!button) return false;
    button.click();
    return true;
  })()`);
}

async function clickProductAction(client, productName, actionText) {
  return client.evaluate(`(() => {
    const productName = ${JSON.stringify(productName)};
    const actionText = ${JSON.stringify(actionText)};
    const candidates = [...document.querySelectorAll(".MuiPaper-root")];
    const card = candidates.find((item) => {
      const hasProduct = item.textContent?.includes(productName);
      const hasAction = [...item.querySelectorAll("button")]
        .some((button) => button.textContent?.trim() === actionText && !button.disabled);
      return hasProduct && hasAction;
    });
    const button = card
      ? [...card.querySelectorAll("button")]
          .find((item) => item.textContent?.trim() === actionText && !item.disabled)
      : null;
    if (!button) return false;
    button.click();
    return true;
  })()`);
}

async function writeDiagnostics(client, name) {
  const page = await Promise.race([
    client.evaluate(`({
      href: location.href,
      bodyText: document.body?.innerText ?? "",
      bodyHtml: document.body?.innerHTML?.slice(0, 30000) ?? "",
    })`),
    sleep(5_000).then(() => ({ unavailable: "CDP diagnostic timeout" })),
  ]);
  await writeFile(
    path.join(artifactDir, `${name}.json`),
    JSON.stringify({ page, productArchiveRequests }, null, 2),
  );
}

async function cleanup() {
  if (cleanupStarted) return;
  cleanupStarted = true;
  activeClient?.close();
  activeClient = undefined;
  await Promise.allSettled([
    activeChrome ? stopProcess(activeChrome) : Promise.resolve(),
    activeVite ? stopProcess(activeVite) : Promise.resolve(),
  ]);
  if (activeApi) {
    await Promise.race([activeApi.close(), sleep(2_000)]);
  }
  await rm(profileDir, {
    recursive: true,
    force: true,
    maxRetries: 10,
    retryDelay: 100,
  });
  activeApi = undefined;
  activeVite = undefined;
  activeChrome = undefined;
}

async function run() {
  await rm(profileDir, {
    recursive: true,
    force: true,
    maxRetries: 10,
    retryDelay: 100,
  });
  await mkdir(artifactDir, { recursive: true });
  activeApi = startProductArchiveApi();
  await activeApi.listen();
  activeVite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5213",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18116" },
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
      "--remote-debugging-port=9265",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9265/json/version");
    const targets = await fetch("http://127.0.0.1:9265/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("product-archive.html"));
    assert.ok(target?.webSocketDebuggerUrl);
    activeClient = await CdpClient.connect(target.webSocketDebuggerUrl);
    await activeClient.send("Runtime.enable");
    await activeClient.send("Page.enable");
    await activeClient.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await activeClient.evaluate("window.confirm = () => true");

    try {
      await waitForExpression(
        activeClient,
        `document.body?.innerText?.includes("Архив продуктов") &&
         document.body?.innerText?.includes("Гречка") &&
         document.body?.innerText?.includes("Рис") &&
         !document.body?.innerText?.includes("Загрузка каталога продуктов")`,
        "loaded active product catalogue",
      );
      assert.equal(await clickProductAction(activeClient, "Гречка", "Архивировать"), true);
      await waitForExpression(
        activeClient,
        `document.body?.innerText?.includes("Продукт «Гречка» перемещён в архив.")`,
        "product archived",
      );
      assert.ok(
        productArchiveRequests.some(
          (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/archive",
        ),
      );

      assert.equal(await clickTextButton(activeClient, "Архив"), true);
      await waitForExpression(
        activeClient,
        `document.body?.innerText?.includes("Заблокирован политикой") &&
         document.body?.innerText?.includes("алкогольные позиции") &&
         document.body?.innerText?.includes("Гречка")`,
        "loaded archived products",
      );
      const lockedState = await activeClient.evaluate(`(() => {
        const card = [...document.querySelectorAll(".MuiPaper-root")]
          .find((item) => item.textContent?.includes("Вино") && item.textContent?.includes("Заблокирован политикой"));
        const restore = card
          ? [...card.querySelectorAll("button")].find((button) => button.textContent?.trim() === "Восстановить")
          : null;
        return Boolean(card && restore?.disabled);
      })()`);
      assert.equal(lockedState, true);

      assert.equal(await clickProductAction(activeClient, "Гречка", "Восстановить"), true);
      await waitForExpression(
        activeClient,
        `document.body?.innerText?.includes("Продукт «Гречка» восстановлен.")`,
        "product restored",
      );
      assert.ok(
        productArchiveRequests.some(
          (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/restore",
        ),
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
        `Horizontal overflow: ${JSON.stringify(layout)}`,
      );
      await writeFile(
        path.join(artifactDir, "product-archive.json"),
        JSON.stringify({ requests: productArchiveRequests, layout }, null, 2),
      );
    } catch (error) {
      await writeDiagnostics(activeClient, "product-archive-diagnostic");
      throw error;
    }

    console.log("Product archive browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

const watchdog = setTimeout(async () => {
  console.error("Product archive browser acceptance timed out.");
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "product-archive-error.txt"),
    "Product archive browser acceptance timed out before completion.\n",
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
    await mkdir(artifactDir, { recursive: true });
    await writeFile(
      path.join(artifactDir, "product-archive-error.txt"),
      `${error?.stack ?? error}\n`,
    );
    await cleanup();
    process.exit(1);
  });
