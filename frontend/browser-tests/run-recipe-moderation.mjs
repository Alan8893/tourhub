import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { requests, startRecipeModerationApi } from "./recipe-moderation-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5192/browser-tests/recipe-moderation.html";
const profileDir = "/tmp/tourhub-recipe-moderation-profile";

async function clickText(client, text, selector = "button") {
  const clicked = await client.evaluate(`(() => {
    const nodes = [...document.querySelectorAll(${JSON.stringify(selector)})];
    const node = nodes.find((item) => item.textContent?.includes(${JSON.stringify(text)}));
    if (!node || node.disabled) return false;
    node.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Control not found: ${text}`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startRecipeModerationApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5192",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18102" },
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
      "--remote-debugging-port=9248",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9248/json/version");
    const targets = await fetch("http://127.0.0.1:9248/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("recipe-moderation.html"));
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
      `document.body?.innerText?.includes("Рецепты")`,
      "loaded recipe page",
    );
    await clickText(client, "На проверке");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Каша на проверку") &&
       document.body?.innerText?.includes("Автор рецепта")`,
      "loaded moderation queue",
    );

    await clickText(client, "Каша на проверку", ".MuiListItemButton-root");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Рецепт отправлен на проверку") &&
       document.body?.innerText?.includes("Отправил: Автор рецепта") &&
       document.body?.innerText?.includes("Опубликовать") &&
       document.body?.innerText?.includes("Отклонить")`,
      "loaded submitted recipe",
    );

    await clickText(client, "Отклонить");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Отклонить публикацию") &&
       document.querySelector('textarea[aria-label="Что нужно исправить"], textarea') !== null`,
      "opened rejection dialog",
    );

    const filled = await client.evaluate(`(() => {
      const input = document.querySelector('textarea[aria-label="Что нужно исправить"], textarea');
      if (!input) return false;
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        "value",
      )?.set;
      setter?.call(input, "Добавьте точное время приготовления.");
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    })()`);
    assert.equal(filled, true, "Rejection comment field not found");

    const dialogRejected = await client.evaluate(`(() => {
      const dialog = document.querySelector('[role="dialog"]');
      const button = [...(dialog?.querySelectorAll("button") ?? [])].find(
        (item) => item.textContent?.trim() === "Отклонить",
      );
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`);
    assert.equal(dialogRejected, true, "Reject dialog action not found");

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Сейчас нет рецептов, ожидающих проверки.")`,
      "empty moderation queue after rejection",
    );

    const rejection = requests.find(
      (item) =>
        item.method === "POST" &&
        item.path === "/api/v1/recipes/recipe-submitted/reject",
    );
    assert.equal(rejection?.body?.comment, "Добавьте точное время приготовления.");

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
    );

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "recipe-moderation-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Recipe moderation browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await api.close();
    await rm(profileDir, { recursive: true, force: true });
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "recipe-moderation-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
