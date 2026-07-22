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
  removeChromeProfile,
  waitForPageTarget,
  waitForRequest,
} from "./guided-release-browser-helpers.mjs";
import { createProjectTeamAccessMockApi } from "./project-team-access-mock-api.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5197;
const apiPort = 18102;
const debuggingPort = 9251;
const pageUrl = `http://127.0.0.1:${frontendPort}/projects`;
const profileDir = `/tmp/tourhub-project-team-access-${process.pid}`;

async function run() {
  await removeChromeProfile(profileDir);
  await mkdir(artifactDir, { recursive: true });
  const mockApi = createProjectTeamAccessMockApi(apiPort);
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
    const target = await waitForPageTarget(debuggingPort, "/projects");
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
      `document.body?.innerText?.includes("Доступный поход") &&
       document.body?.innerText?.includes("Показывать завершённые")`,
      "scoped project catalogue",
    );
    let text = await client.evaluate("document.body.innerText");
    assert.equal(text.includes("Завершённый поход"), false);
    assert.ok(text.includes("Владелец: Иван Владелец"));

    const checked = await client.evaluate(`(() => {
      const label = [...document.querySelectorAll("label")]
        .find((item) => item.textContent?.includes("Показывать завершённые"));
      const input = label?.querySelector('input[type="checkbox"]');
      if (!input) return false;
      input.click();
      return true;
    })()`);
    assert.equal(checked, true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Завершённый поход")`,
      "completed project filter",
    );

    await client.evaluate(`location.href = ${JSON.stringify(
      `http://127.0.0.1:${frontendPort}/projects/77/menu`,
    )}`);
    await waitForExpression(
      client,
      `location.pathname === "/projects/77/menu" &&
       document.body?.innerText?.includes("Меню доступно только для просмотра") &&
       document.body?.innerText?.includes("Плов походный")`,
      "collaborator read-only menu",
      20_000,
    );
    text = await client.evaluate("document.body.innerText");
    assert.ok(text.includes("Вы приглашены в команду проекта"));
    assert.equal(text.includes("Настройки проекта"), false);
    assert.equal(text.includes("Добавить блюдо"), false);
    assert.equal(text.includes("Сформировать меню"), false);
    assert.equal(text.includes("Подготовить проект"), false);

    await client.evaluate(`location.href = ${JSON.stringify(
      `http://127.0.0.1:${frontendPort}/projects/77`,
    )}`);
    await waitForExpression(
      client,
      `location.pathname === "/projects/77" &&
       document.body?.innerText?.includes("Команда проекта") &&
       document.body?.innerText?.includes("Иван Владелец") &&
       document.body?.innerText?.includes("Анна Приглашённая")`,
      "project-scoped contacts",
      20_000,
    );
    text = await client.evaluate("document.body.innerText");
    for (const expected of [
      "Владелец проекта",
      "Дополнительный инструктор",
      "Позвонить: +79991112233",
      "Telegram",
      "MAX",
      "VK",
      "Сохранить контакт",
    ]) {
      assert.ok(text.includes(expected), `Missing Project contact action: ${expected}`);
    }

    assert.equal(await clickButton(client, "Сохранить контакт"), true);
    await waitForRequest(
      mockApi.requests,
      "GET",
      "/api/v1/projects/77/team/1/vcard",
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
      `Horizontal overflow at 360px: ${JSON.stringify(layout)}`,
    );
    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "project-team-access-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );

    client.close();
    console.log("Project team access browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await mockApi.close();
    await removeChromeProfile(profileDir, { allowResidual: true });
    await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "project-team-access-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
