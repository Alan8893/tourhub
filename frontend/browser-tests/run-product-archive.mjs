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
  waitForHttp,
} from "./club-settings-cdp.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5213/browser-tests/product-archive.html";
const profileDir = `/tmp/tourhub-product-archive-${process.pid}`;
const scenarioTimeoutMs = 75_000;
const cdpTimeoutMs = 20_000;

let activeApi;
let activeVite;
let activeChrome;
let activeClient;
let cleanupStarted = false;

async function bounded(promise, description, timeoutMs = cdpTimeoutMs) {
  return Promise.race([
    promise,
    sleep(timeoutMs).then(() => {
      throw new Error(`Timed out during ${description}`);
    }),
  ]);
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
    console.log("Product archive acceptance: connecting to Chrome.");
    await waitForHttp("http://127.0.0.1:9265/json/version");
    const targets = await fetch("http://127.0.0.1:9265/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("product-archive.html"));
    assert.ok(target?.webSocketDebuggerUrl);
    activeClient = await bounded(
      CdpClient.connect(target.webSocketDebuggerUrl),
      "CDP connection",
    );
    await bounded(activeClient.send("Runtime.enable"), "Runtime.enable");
    await bounded(activeClient.send("Page.enable"), "Page.enable");
    await bounded(
      activeClient.send("Emulation.setDeviceMetricsOverride", {
        width: 1280,
        height: 900,
        deviceScaleFactor: 1,
        mobile: false,
      }),
      "desktop metrics",
    );

    console.log("Product archive acceptance: running browser workflow.");
    const workflow = await bounded(
      activeClient.evaluate(`(async () => {
        const sleep = (milliseconds) =>
          new Promise((resolve) => setTimeout(resolve, milliseconds));
        const waitFor = async (predicate, description) => {
          const deadline = Date.now() + 15000;
          while (Date.now() < deadline) {
            if (predicate()) return;
            await sleep(100);
          }
          throw new Error("Timed out waiting for " + description);
        };
        const clickButton = (text) => {
          const button = [...document.querySelectorAll("button")]
            .find((item) => item.textContent?.trim() === text && !item.disabled);
          if (!button) throw new Error("Button not found: " + text);
          button.click();
        };
        const clickProductAction = (productName, actionText) => {
          const card = [...document.querySelectorAll(".MuiPaper-root")]
            .find((item) => {
              const hasProduct = item.textContent?.includes(productName);
              const hasAction = [...item.querySelectorAll("button")]
                .some((button) =>
                  button.textContent?.trim() === actionText && !button.disabled
                );
              return hasProduct && hasAction;
            });
          const button = card
            ? [...card.querySelectorAll("button")]
                .find((item) =>
                  item.textContent?.trim() === actionText && !item.disabled
                )
            : null;
          if (!button) {
            throw new Error("Product action not found: " + productName + " / " + actionText);
          }
          button.click();
        };

        window.confirm = () => true;
        await waitFor(
          () => document.body?.innerText?.includes("Архив продуктов") &&
            document.body?.innerText?.includes("Гречка") &&
            document.body?.innerText?.includes("Рис") &&
            !document.body?.innerText?.includes("Загрузка каталога продуктов"),
          "active product catalogue",
        );

        clickProductAction("Гречка", "Архивировать");
        await waitFor(
          () => document.body?.innerText?.includes("Продукт «Гречка» перемещён в архив."),
          "archive success",
        );

        clickButton("Архив");
        await waitFor(
          () => document.body?.innerText?.includes("Заблокирован политикой") &&
            document.body?.innerText?.includes("алкогольные позиции") &&
            document.body?.innerText?.includes("Гречка"),
          "archived product catalogue",
        );

        const policyCard = [...document.querySelectorAll(".MuiPaper-root")]
          .find((item) =>
            item.textContent?.includes("Вино") &&
            item.textContent?.includes("Заблокирован политикой")
          );
        const policyRestore = policyCard
          ? [...policyCard.querySelectorAll("button")]
              .find((button) => button.textContent?.trim() === "Восстановить")
          : null;
        if (!policyCard || !policyRestore?.disabled) {
          throw new Error("Policy-locked Product restore is not disabled");
        }

        clickProductAction("Гречка", "Восстановить");
        await waitFor(
          () => document.body?.innerText?.includes("Продукт «Гречка» восстановлен."),
          "restore success",
        );

        return {
          policyLocked: true,
          bodyText: document.body?.innerText ?? "",
        };
      })()`),
      "Product archive browser workflow",
      55_000,
    );
    assert.equal(workflow.policyLocked, true);
    assert.ok(
      productArchiveRequests.some(
        (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/archive",
      ),
    );
    assert.ok(
      productArchiveRequests.some(
        (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/restore",
      ),
    );

    await bounded(
      activeClient.send("Emulation.setDeviceMetricsOverride", {
        width: 360,
        height: 900,
        deviceScaleFactor: 1,
        mobile: true,
      }),
      "mobile metrics",
    );
    await sleep(350);
    const layout = await bounded(
      activeClient.evaluate(`({
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        bodyScrollWidth: document.body.scrollWidth,
      })`),
      "mobile layout",
    );
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
      `Horizontal overflow: ${JSON.stringify(layout)}`,
    );

    await writeFile(
      path.join(artifactDir, "product-archive.json"),
      JSON.stringify(
        { workflow, requests: productArchiveRequests, layout },
        null,
        2,
      ),
    );
    console.log("Product archive browser acceptance passed.");
  } catch (error) {
    await writeFile(
      path.join(artifactDir, "product-archive-error.txt"),
      `${error?.stack ?? error}\n`,
    );
    throw error;
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
    await cleanup();
    process.exit(1);
  });
