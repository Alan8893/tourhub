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
  selectMuiOption,
  setFieldByLabel,
} from "./invitation-settings-actions.mjs";
import { requests, startMailSettingsApi } from "./mail-settings-fixture.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5186/browser-tests/mail-settings.html";
const profileDir = "/tmp/tourhub-mail-settings-profile";

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startMailSettingsApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5186",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18088" },
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
      "--remote-debugging-port=9238",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9238/json/version");
    const targets = await fetch("http://127.0.0.1:9238/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("mail-settings.html"));
    assert.ok(target?.webSocketDebuggerUrl);
    const client = await CdpClient.connect(target.webSocketDebuggerUrl);
    await client.send("Runtime.enable");
    await client.send("Page.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1100,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await sleep(250);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Почта") &&
       document.body?.innerText?.includes("TOURHUB_SMTP_SECRET") &&
       document.body?.innerText?.includes("Настроен в environment") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Отправить тестовое письмо" && item.disabled,
       )`,
      "loaded mail boundary editor",
    );

    assert.equal(await client.evaluate(`document.querySelector('input[type="password"]')`), null);
    assert.equal(await setFieldByLabel(client, "SMTP host", " SMTP.Example.COM. "), true);
    assert.equal(await setFieldByLabel(client, "SMTP-порт", "465"), true);
    await selectMuiOption(client, "Защита соединения", "TLS с момента подключения");
    assert.equal(await setFieldByLabel(client, "Имя пользователя SMTP", " mailer "), true);
    assert.equal(await setFieldByLabel(client, "Адрес отправителя", "TourHub@Example.COM"), true);
    assert.equal(await setFieldByLabel(client, "Имя отправителя", "Турклуб"), true);
    assert.equal(await setFieldByLabel(client, "Reply-To", "support@Example.COM"), true);
    assert.equal(await setFieldByLabel(client, "Тестовый адрес", "admin@Example.COM"), true);
    assert.equal(await setFieldByLabel(client, "Тайм-аут, секунд", "45"), true);
    assert.equal(await setFieldByLabel(client, "Повторные попытки", "5"), true);
    assert.equal(await clickButton(client, "Сохранить раздел"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Несекретные настройки почты сохранены") &&
       document.body?.innerText?.includes("SMTP host") &&
       document.body?.innerText?.includes("тестовый адрес") &&
       document.body?.innerText?.includes("Текущая версия: 2") &&
       [...document.querySelectorAll('input')].some(
         (item) => item.value === "smtp.example.com",
       )`,
      "saved mail boundary settings",
    );

    const update = requests.find(
      (item) => item.method === "PUT" && item.path === "/api/v1/settings/mail",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.smtp_host, " SMTP.Example.COM. ");
    assert.equal(update?.body.smtp_port, 465);
    assert.equal(update?.body.security_mode, "tls");
    assert.equal(update?.body.smtp_username, "mailer");
    assert.equal(update?.body.sender_email, "TourHub@Example.COM");
    assert.equal(update?.body.sender_name, "Турклуб");
    assert.equal(update?.body.reply_to_email, "support@Example.COM");
    assert.equal(update?.body.test_recipient_email, "admin@Example.COM");
    assert.equal(update?.body.timeout_seconds, 45);
    assert.equal(update?.body.retry_count, 5);
    assert.equal(
      Object.keys(update?.body ?? {}).some(
        (key) => key.includes("secret") || key.includes("credential"),
      ),
      false,
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
    );

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "mail-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Mail settings browser acceptance passed.");
  } finally {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await api.close();
    await rm(profileDir, { recursive: true, force: true });
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(path.join(artifactDir, "mail-settings-error.txt"), `${error?.stack ?? error}\n`);
  process.exitCode = 1;
});
