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
import { requests, startInvitationSettingsApi } from "./invitation-settings-fixture.mjs";
import {
  clickButton,
  clickLabel,
  selectMuiOption,
  setFieldByLabel,
} from "./invitation-settings-actions.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5185/browser-tests/invitation-settings.html";
const profileDir = "/tmp/tourhub-invitation-settings-profile";

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startInvitationSettingsApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5185",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18087" },
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
      "--remote-debugging-port=9237",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9237/json/version");
    const targets = await fetch("http://127.0.0.1:9237/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("invitation-settings.html"));
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
    await sleep(250);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Политика приглашений") &&
       document.body?.innerText?.includes("Рабочие приглашения") &&
       document.body?.innerText?.includes("Только администраторы") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Сохранить раздел",
       )`,
      "loaded invitation policy editor",
    );

    assert.equal(
      await client.evaluate(
        `document.querySelector('input[aria-label="Только администраторы"]')?.disabled`,
      ),
      true,
    );
    assert.equal(await setFieldByLabel(client, "Срок действия, дней", "14"), true);
    assert.equal(await setFieldByLabel(client, "Лимит активных приглашений", "25"), true);
    assert.equal(
      await setFieldByLabel(
        client,
        "Разрешённые email-домены",
        "Example.COM\nexample.com\nпример.рф",
      ),
      true,
    );
    await selectMuiOption(client, "Роль по умолчанию", "Проверенный инструктор");
    assert.equal(await clickLabel(client, "Разрешить повторную отправку"), true);
    assert.equal(await clickLabel(client, "Требовать подтверждение email"), true);
    assert.equal(await clickButton(client, "Сохранить раздел"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Политика приглашений сохранена") &&
       document.body?.innerText?.includes("роль приглашённого по умолчанию") &&
       document.body?.innerText?.includes("разрешённые email-домены") &&
       document.body?.innerText?.includes("Текущая версия: 2") &&
       document.querySelector('textarea')?.value?.includes("xn--e1afmkfd.xn--p1ai")`,
      "saved normalized invitation policy",
    );

    const update = requests.find(
      (item) => item.method === "PUT" && item.path === "/api/v1/settings/invitations",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.expires_after_days, 14);
    assert.equal(update?.body.default_role, "verified_instructor");
    assert.deepEqual(update?.body.allowed_email_domains, [
      "Example.COM",
      "example.com",
      "пример.рф",
    ]);
    assert.equal(update?.body.allow_resend, false);
    assert.equal(update?.body.active_invitation_limit, 25);
    assert.equal(update?.body.administrators_only, true);
    assert.equal(update?.body.require_email_confirmation, false);

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
      path.join(artifactDir, "invitation-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Invitation settings browser acceptance passed.");
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
    path.join(artifactDir, "invitation-settings-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
