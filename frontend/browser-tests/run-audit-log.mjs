import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { auditRequests, startAuditLogApi } from "./audit-log-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5192/browser-tests/audit-log.html";
const profileDir = "/tmp/tourhub-audit-log-profile";
const normalizeText = (value) =>
  String(value ?? "")
    .normalize("NFKC")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/\s+/g, " ")
    .trim();

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startAuditLogApi();
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
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18095" },
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
      "--remote-debugging-port=9244",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9244/json/version");
    const targets = await fetch("http://127.0.0.1:9244/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("audit-log.html"));
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
      `document.body?.innerText?.includes("Аудит действий") &&
       document.body?.innerText?.includes("Анна Администратор") &&
       document.body?.innerText?.includes("Найдено записей: 5")`,
      "loaded audit event collection",
    );
    const loadedText = normalizeText(await client.evaluate("document.body.innerText"));
    for (const label of [
      "Меню сгенерировано",
      "Блюдо заменено в приёме пищи",
      "Приём пищи",
      "Подготовка проекта выполнена",
      "Рецепт отклонён",
      "Роль пользователя изменена",
      "Журнал не содержит пароли",
    ]) {
      assert.ok(
        loadedText.includes(normalizeText(label)),
        `Missing audit label: ${label}\nRendered text:\n${loadedText}`,
      );
    }

    const filtered = await client.evaluate(`(() => {
      const input = document.querySelector('input[placeholder="Например: meal_plan_generated"]');
      if (!input) return false;
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
      setter?.call(input, "meal_slot_dish_replaced");
      input.dispatchEvent(new Event("input", { bubbles: true }));
      const button = [...document.querySelectorAll("button")].find(
        (item) => item.textContent?.trim() === "Применить фильтры",
      );
      button?.click();
      return Boolean(button);
    })()`);
    assert.equal(filtered, true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Найдено записей: 1") &&
       document.body?.innerText?.includes("Анна Администратор")`,
      "filtered MealSlot audit history",
    );
    const filteredText = normalizeText(await client.evaluate("document.body.innerText"));
    assert.ok(filteredText.includes(normalizeText("Блюдо заменено в приёме пищи")));
    assert.ok(filteredText.includes(normalizeText("Приём пищи")));
    assert.ok(!filteredText.includes(normalizeText("Меню сгенерировано")));
    assert.ok(!filteredText.includes(normalizeText("Подготовка проекта выполнена")));
    assert.ok(!filteredText.includes(normalizeText("Рецепт отклонён")));
    assert.ok(
      auditRequests.some(
        (request) =>
          request.path === "/api/v1/audit/events" &&
          request.query.action === "meal_slot_dish_replaced",
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
      path.join(artifactDir, "audit-log-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Audit log browser acceptance passed.");
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
    path.join(artifactDir, "audit-log-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
