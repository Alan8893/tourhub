import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { requests, startAccountAdminApi } from "./account-admin-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5189/browser-tests/account-admin.html";
const profileDir = "/tmp/tourhub-account-admin-profile";

async function selectRole(client, email, optionText) {
  const opened = await client.evaluate(`(() => {
    const emailNode = [...document.querySelectorAll("p")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(email)},
    );
    const card = emailNode?.closest(".MuiPaper-root");
    const control = card?.querySelector('[role="combobox"]');
    if (!control) return false;
    control.dispatchEvent(new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 0,
    }));
    return true;
  })()`);
  assert.equal(opened, true, `Role selector not found for ${email}`);
  await waitForExpression(
    client,
    `[...document.querySelectorAll('[role="option"]')].some(
      (item) => item.textContent?.trim() === ${JSON.stringify(optionText)},
    )`,
    `role option ${optionText}`,
  );
  const selected = await client.evaluate(`(() => {
    const option = [...document.querySelectorAll('[role="option"]')].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(optionText)},
    );
    if (!option) return false;
    option.click();
    return true;
  })()`);
  assert.equal(selected, true, `Role option not found: ${optionText}`);
}

async function toggleActive(client, email) {
  return client.evaluate(`(() => {
    const control = document.querySelector(
      'input[aria-label=${JSON.stringify(`Активен ${email}`)}]',
    );
    if (!control) return false;
    control.click();
    return true;
  })()`);
}

async function saveCard(client, email) {
  return client.evaluate(`(() => {
    window.confirm = () => true;
    const emailNode = [...document.querySelectorAll("p")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(email)},
    );
    const card = emailNode?.closest(".MuiPaper-root");
    const button = [...(card?.querySelectorAll("button") ?? [])].find(
      (item) => item.textContent?.trim() === "Сохранить пользователя",
    );
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startAccountAdminApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5189",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18092" },
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
      "--remote-debugging-port=9241",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9241/json/version");
    const targets = await fetch("http://127.0.0.1:9241/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("account-admin.html"));
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
      `document.body?.innerText?.includes("Пользователи") &&
       document.body?.innerText?.includes("member@example.org") &&
       document.body?.innerText?.includes("Текущая учётная запись") &&
       document.body?.innerText?.includes("последнего активного администратора")`,
      "loaded account administration",
    );

    await selectRole(client, "member@example.org", "Проверенный инструктор");
    assert.equal(await toggleActive(client, "member@example.org"), true);
    assert.equal(await saveCard(client, "member@example.org"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Изменения пользователя сохранены") &&
       document.body?.innerText?.includes("Отключён") &&
       document.body?.innerText?.includes("Роль: Проверенный инструктор") &&
       document.body?.innerText?.includes("Версия: 2")`,
      "saved account changes",
    );

    const update = requests.find(
      (item) => item.method === "PATCH" && item.path === "/api/v1/users/2",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.role, "verified_instructor");
    assert.equal(update?.body.is_active, false);

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
      path.join(artifactDir, "account-admin-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Account administration browser acceptance passed.");
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
    path.join(artifactDir, "account-admin-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
