import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { requests, startModuleSettingsApi } from "./module-settings-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5184/browser-tests/module-settings.html";
const profileDir = "/tmp/tourhub-module-settings-profile";

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

async function clickSwitch(client, label) {
  return client.evaluate(`(() => {
    const input = document.querySelector(
      'input[aria-label=${JSON.stringify(label)}]',
    );
    if (!input || input.disabled) return false;
    input.click();
    return true;
  })()`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startModuleSettingsApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5184",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18086" },
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
      "--remote-debugging-port=9236",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9236/json/version");
    const targets = await fetch("http://127.0.0.1:9236/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("module-settings.html"));
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
      `document.body?.innerText?.includes("Переключатели скрывают навигацию") &&
       document.body?.innerText?.includes("Модуль «Проекты» обязателен") &&
       document.body?.innerText?.includes("Карточка документов видима")`,
      "loaded module editor",
    );

    assert.equal(
      await client.evaluate(`document.querySelector('input[aria-label="Проекты"]')?.disabled`),
      true,
    );
    assert.equal(await clickSwitch(client, "Документы"), true);
    await waitForExpression(
      client,
      `!document.querySelector('input[aria-label="Закупка"]')?.disabled &&
       !document.querySelector('input[aria-label="Оборудование"]')?.disabled`,
      "document dependencies unlocked",
    );
    assert.equal(await clickSwitch(client, "Закупка"), true);
    assert.equal(await clickSwitch(client, "Оборудование"), true);
    assert.equal(await clickSwitch(client, "Импорт"), true);
    assert.equal(await clickByText(client, "Сохранить раздел"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Видимость модулей сохранена и применена без перезапуска") &&
       document.body?.innerText?.includes("видимость документов") &&
       !document.body?.innerText?.includes("Карточка закупки видима") &&
       !document.body?.innerText?.includes("Карточка оборудования видима") &&
       !document.body?.innerText?.includes("Карточка документов видима")`,
      "saved module visibility",
    );

    const update = requests.find(
      (item) => item.method === "PUT" && item.path === "/api/v1/settings/modules",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.catalog_import_visible, false);
    assert.equal(update?.body.shopping_visible, false);
    assert.equal(update?.body.equipment_visible, false);
    assert.equal(update?.body.documents_visible, false);

    const desktopDrawer = await client.evaluate(`(() => {
      const drawers = [...document.querySelectorAll('.MuiDrawer-root')].filter(
        (item) => getComputedStyle(item).display !== 'none',
      );
      return drawers.map((item) => item.textContent ?? '').join(' ');
    })()`);
    assert.ok(desktopDrawer.includes("Проекты"));
    assert.ok(desktopDrawer.includes("Блюда"));
    assert.ok(desktopDrawer.includes("Рецепты"));
    assert.ok(desktopDrawer.includes("Настройки"));
    assert.equal(desktopDrawer.includes("Импорт"), false);

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(400);
    assert.equal(await clickByText(client, "Открыть мобильное меню"), true);
    await waitForExpression(
      client,
      `[...document.querySelectorAll('.MuiDrawer-root')].some(
        (item) => getComputedStyle(item).display !== 'none' && item.textContent?.includes('Проекты'),
      )`,
      "mobile module navigation",
    );
    const mobileLayout = await client.evaluate(`(() => {
      const visibleDrawer = [...document.querySelectorAll('.MuiDrawer-root')].find(
        (item) => getComputedStyle(item).display !== 'none' && item.textContent?.includes('Проекты'),
      );
      return {
        clientWidth: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        bodyScrollWidth: document.body.scrollWidth,
        drawerText: visibleDrawer?.textContent ?? '',
      };
    })()`);
    assert.ok(
      mobileLayout.scrollWidth <= mobileLayout.clientWidth + 1 &&
        mobileLayout.bodyScrollWidth <= mobileLayout.clientWidth + 1,
    );
    assert.equal(mobileLayout.drawerText.includes("Импорт"), false);
    assert.ok(mobileLayout.drawerText.includes("Настройки"));

    await client.evaluate(`(() => {
      window.history.pushState({}, '', '/catalog-import');
      window.dispatchEvent(new PopStateEvent('popstate'));
      return true;
    })()`);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Прямой маршрут импорта доступен")`,
      "hidden direct route remains available",
    );

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "module-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Module settings browser acceptance passed.");
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
    path.join(artifactDir, "module-settings-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
