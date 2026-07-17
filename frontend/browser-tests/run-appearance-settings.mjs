import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { requests, startAppearanceApi } from "./appearance-settings-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5182/browser-tests/appearance-settings.html";
const profileDir = "/tmp/tourhub-appearance-settings-profile";

async function clickByText(client, text, selector = "button") {
  return client.evaluate(`(() => {
    const element = [...document.querySelectorAll(${JSON.stringify(selector)})].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(text)},
    );
    if (!element || element.disabled) return false;
    element.click();
    return true;
  })()`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startAppearanceApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5182",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18084" },
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
      "--remote-debugging-port=9234",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9234/json/version");
    const targets = await fetch("http://127.0.0.1:9234/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("appearance-settings.html"));
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
    await sleep(200);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Оформление") &&
       document.body?.innerText?.includes("Живой предпросмотр") &&
       document.body?.innerText?.includes("Предустановки") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Экспортировать тему",
       )`,
      "loaded appearance editor",
    );

    assert.equal(await clickByText(client, "Океан"), true);
    assert.equal(await clickByText(client, "Тёмная"), true);
    await waitForExpression(
      client,
      `[...document.querySelectorAll("button")].some(
        (item) => item.textContent?.trim() === "Тёмная" &&
          item.getAttribute("aria-pressed") === "true",
      )`,
      "dark isolated preview",
    );

    assert.equal(await clickByText(client, "Сохранить раздел"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Оформление сохранено и применено без перезапуска") &&
       document.body?.innerText?.includes("светлая тема: primary")`,
      "saved appearance and history",
    );

    const update = requests.find(
      (item) => item.method === "PUT" && item.path === "/api/v1/settings/appearance",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.preset_name, "ocean");
    assert.equal(update?.body.light.primary, "#075985");

    assert.equal(
      await client.evaluate(`(() => {
        const combo = [...document.querySelectorAll('[role="combobox"]')].find(
          (item) => item.getAttribute("aria-labelledby")?.includes("display-mode-label"),
        );
        if (!combo) return false;
        combo.click();
        return true;
      })()`),
      true,
    );
    await waitForExpression(
      client,
      `[...document.querySelectorAll('[role="option"]')].some(
        (item) => item.textContent?.trim() === "Тёмная тема",
      )`,
      "personal display modes",
    );
    assert.equal(
      await client.evaluate(`(() => {
        const option = [...document.querySelectorAll('[role="option"]')].find(
          (item) => item.textContent?.trim() === "Тёмная тема",
        );
        if (!option) return false;
        option.click();
        return true;
      })()`),
      true,
    );
    await waitForExpression(
      client,
      `localStorage.getItem("tourhub.display-mode") === "dark" &&
       getComputedStyle(document.body).backgroundColor === "rgb(11, 21, 27)"`,
      "saved dark preference and global theme",
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(450);
    const layout = await client.evaluate(`(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
      hasPreview: document.body?.innerText?.includes("Предпросмотр TourHub"),
      hasImport: [...document.querySelectorAll("button")].some(
        (item) => item.textContent?.trim() === "Импортировать тему",
      ),
    }))()`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
    );
    assert.equal(layout.hasPreview, true);
    assert.equal(layout.hasImport, true);

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "appearance-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Appearance settings browser acceptance passed.");
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
    path.join(artifactDir, "appearance-settings-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
