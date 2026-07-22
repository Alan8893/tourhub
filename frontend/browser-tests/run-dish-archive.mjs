import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  dishArchiveRequests,
  startDishArchiveApi,
} from "./dish-archive-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5214/browser-tests/dish-archive.html";
const profileDir = `/tmp/tourhub-dish-archive-${process.pid}`;

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

async function clickDishAction(client, dishName, actionText) {
  return client.evaluate(`(() => {
    const dishName = ${JSON.stringify(dishName)};
    const actionText = ${JSON.stringify(actionText)};
    const candidates = [...document.querySelectorAll(".MuiPaper-root")];
    const card = candidates.find((item) => {
      const hasDish = item.textContent?.includes(dishName);
      const hasAction = [...item.querySelectorAll("button")]
        .some((button) => button.textContent?.trim() === actionText && !button.disabled);
      return hasDish && hasAction;
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
    JSON.stringify({ page, dishArchiveRequests }, null, 2),
  );
  const screenshot = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  await writeFile(path.join(artifactDir, `${name}.png`), Buffer.from(screenshot.data, "base64"));
}

async function run() {
  await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  await mkdir(artifactDir, { recursive: true });
  const api = startDishArchiveApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5214",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18117" },
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
      "--remote-debugging-port=9266",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9266/json/version");
    const targets = await fetch("http://127.0.0.1:9266/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("dish-archive.html"));
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
        `document.body?.innerText?.includes("Архив блюд") &&
         document.body?.innerText?.includes("Гречневая каша") &&
         document.body?.innerText?.includes("Овощной суп") &&
         !document.body?.innerText?.includes("Загрузка каталога блюд")`,
        "loaded active dish catalogue",
      );
      assert.equal(await clickDishAction(client, "Гречневая каша", "Архивировать"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Блюдо «Гречневая каша» перемещено в архив.")`,
        "dish archived",
      );
      assert.ok(
        dishArchiveRequests.some(
          (item) =>
            item.method === "POST" &&
            item.path === "/api/v1/dishes/buckwheat-dish/archive",
        ),
      );

      assert.equal(await clickTextButton(client, "Архив"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Заблокировано политикой") &&
         document.body?.innerText?.includes("алкогольными") &&
         document.body?.innerText?.includes("Гречневая каша")`,
        "loaded archived dishes",
      );
      const lockedState = await client.evaluate(`(() => {
        const card = [...document.querySelectorAll(".MuiPaper-root")]
          .find((item) => item.textContent?.includes("Глинтвейн") && item.textContent?.includes("Заблокировано политикой"));
        const restore = card
          ? [...card.querySelectorAll("button")].find((button) => button.textContent?.trim() === "Восстановить")
          : null;
        return Boolean(card && restore?.disabled);
      })()`);
      assert.equal(lockedState, true);

      assert.equal(await clickDishAction(client, "Гречневая каша", "Восстановить"), true);
      await waitForExpression(
        client,
        `document.body?.innerText?.includes("Блюдо «Гречневая каша» восстановлено.")`,
        "dish restored",
      );
      assert.ok(
        dishArchiveRequests.some(
          (item) =>
            item.method === "POST" &&
            item.path === "/api/v1/dishes/buckwheat-dish/restore",
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
      const screenshot = await client.send("Page.captureScreenshot", {
        format: "png",
        captureBeyondViewport: false,
      });
      await writeFile(
        path.join(artifactDir, "dish-archive-mobile.png"),
        Buffer.from(screenshot.data, "base64"),
      );
    } catch (error) {
      await writeDiagnostics(client, "dish-archive-diagnostic");
      throw error;
    }

    client.close();
    console.log("Dish archive browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await api.close();
    await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "dish-archive-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
