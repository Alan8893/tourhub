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

async function captureScreenshot(client, filename) {
  const screenshot = await Promise.race([
    client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    }),
    sleep(5_000).then(() => null),
  ]);
  if (!screenshot?.data) {
    console.warn(`Skipped ${filename}: Chrome screenshot timed out after assertions.`);
    return;
  }
  await writeFile(path.join(artifactDir, filename), Buffer.from(screenshot.data, "base64"));
}

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
  const page = await client.evaluate(`({
    href: location.href,
    bodyText: document.body?.innerText ?? "",
    bodyHtml: document.body?.innerHTML?.slice(0, 30000) ?? "",
  })`);
  await writeFile(
    path.join(artifactDir, `${name}.json`),
    JSON.stringify({ page, productArchiveRequests }, null, 2),
  );
  await captureScreenshot(client, `${name}.png`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  await mkdir(artifactDir, { recursive: true });
  const api = startProductArchiveApi();
  await api.listen();
  const vite = spawn(
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
  const chrome = spawn(
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
    const client = await CdpClient.connect(target.webSocketDebuggerUrl);
    await client.send("Runtime.enable");
    await client.send("Page.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await client.evaluate("window.confirm = () => true");

    try {
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Архив продуктов") &&
         document.body?.innerText?.includes("Гречка") &&
         document.body?.innerText?.includes("Рис") &&
         !document.body?.innerText?.includes("Загрузка каталога продуктов")`,
        "loaded active product catalogue",
      );
      assert.equal(await clickProductAction(client, "Гречка", "Архивировать"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Продукт «Гречка» перемещён в архив.")`,
        "product archived",
      );
      assert.ok(
        productArchiveRequests.some(
          (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/archive",
        ),
      );

      assert.equal(await clickTextButton(client, "Архив"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Заблокирован политикой") &&
         document.body?.innerText?.includes("алкогольные позиции") &&
         document.body?.innerText?.includes("Гречка")`,
        "loaded archived products",
      );
      const lockedState = await client.evaluate(`(() => {
        const card = [...document.querySelectorAll(".MuiPaper-root")]
          .find((item) => item.textContent?.includes("Вино") && item.textContent?.includes("Заблокирован политикой"));
        const restore = card
          ? [...card.querySelectorAll("button")].find((button) => button.textContent?.trim() === "Восстановить")
          : null;
        return Boolean(card && restore?.disabled);
      })()`);
      assert.equal(lockedState, true);

      assert.equal(await clickProductAction(client, "Гречка", "Восстановить"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Продукт «Гречка» восстановлен.")`,
        "product restored",
      );
      assert.ok(
        productArchiveRequests.some(
          (item) => item.method === "POST" && item.path === "/api/v1/products/buckwheat/restore",
        ),
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
      await captureScreenshot(client, "product-archive-mobile.png");
    } catch (error) {
      await writeDiagnostics(client, "product-archive-diagnostic");
      throw error;
    }

    client.close();
    console.log("Product archive browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await Promise.race([api.close(), sleep(2_000)]);
    await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

run()
  .then(() => process.exit(0))
  .catch(async (error) => {
    console.error(error);
    await mkdir(artifactDir, { recursive: true });
    await writeFile(
      path.join(artifactDir, "product-archive-error.txt"),
      `${error?.stack ?? error}\n`,
    );
    process.exit(1);
  });
