import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { accountRequests, startAccountProfileApi } from "./account-profile-fixture.mjs";
import {
  CdpClient,
  findChromeExecutable,
  sleep,
  stopProcess,
  waitForExpression,
  waitForHttp,
} from "./club-settings-cdp.mjs";
import { clickButton, setFieldByLabel } from "./invitation-settings-actions.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5195/browser-tests/account-profile.html";
const profileDir = `/tmp/tourhub-account-profile-${process.pid}`;
const currentPassword = "current-account-password";
const newPassword = "new-account-password-12345";

async function run() {
  await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 });
  await mkdir(artifactDir, { recursive: true });
  const api = startAccountProfileApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5195",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18098" },
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
      "--remote-debugging-port=9247",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9247/json/version");
    const targets = await fetch("http://127.0.0.1:9247/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("account-profile.html"));
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
      `document.body?.innerText?.includes("Личный кабинет") &&
       document.body?.innerText?.includes("Ирина Инструктор") &&
       document.body?.innerText?.includes("Борис Инструктор") &&
       document.body?.innerText?.includes("Смена пароля") &&
       document.body?.innerText?.includes("Сохранить контакт") &&
       document.querySelector('[aria-label="Открыть личный кабинет. Ирина Инструктор. Роль: Инструктор."]')`,
      "loaded personal account",
    );

    const emailReadOnly = await client.evaluate(`(() => {
      const label = [...document.querySelectorAll("label")].find((item) => item.textContent?.includes("Почта"));
      const input = label ? document.getElementById(label.getAttribute("for")) : null;
      return Boolean(input?.readOnly && input.value === "irina@club.example");
    })()`);
    assert.equal(emailReadOnly, true);

    assert.equal(await setFieldByLabel(client, "ФИО", "Ирина Новая"), true);
    assert.equal(await setFieldByLabel(client, "Телефон", "+7 (999) 123-45-67"), true);
    assert.equal(await setFieldByLabel(client, "Telegram", "@irina_guide"), true);
    assert.equal(await setFieldByLabel(client, "MAX", "irina-guide"), true);
    assert.equal(await setFieldByLabel(client, "VK", "https://vk.com/irina-guide"), true);
    assert.equal(await clickButton(client, "Сохранить профиль"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Профиль сохранён.") &&
       document.body?.innerText?.includes("Ирина Новая") &&
       document.querySelector('[aria-label="Открыть личный кабинет. Ирина Новая. Роль: Инструктор."]')`,
      "saved personal profile",
    );
    const profileRequest = accountRequests.find(
      (item) => item.method === "PATCH" && item.path === "/api/v1/account",
    );
    assert.equal(profileRequest?.body.display_name, "Ирина Новая");
    assert.equal(profileRequest?.body.phone, "+7 (999) 123-45-67");
    assert.equal("email" in (profileRequest?.body ?? {}), false);

    const phoneLink = await client.evaluate(`(() => {
      const link = [...document.querySelectorAll("a")].find(
        (item) => item.textContent?.includes("+491234567890"),
      );
      return link?.getAttribute("href") ?? null;
    })()`);
    assert.equal(phoneLink, "tel:+491234567890");

    const contactClicked = await client.evaluate(`(() => {
      const heading = [...document.querySelectorAll("h6")].find(
        (item) => item.textContent?.includes("Борис Инструктор"),
      );
      const card = heading?.closest(".MuiPaper-root");
      const button = [...(card?.querySelectorAll("button") ?? [])].find(
        (item) => item.textContent?.trim() === "Сохранить контакт",
      );
      button?.click();
      return Boolean(button);
    })()`);
    assert.equal(contactClicked, true);
    await waitForExpression(
      client,
      `globalThis.fetch && document.body?.innerText?.includes("Борис Инструктор")`,
      "contact download completed",
    );
    await sleep(250);
    assert.ok(
      accountRequests.some(
        (item) => item.method === "GET" && item.path === "/api/v1/account/contacts/2/vcard",
      ),
    );

    assert.equal(await setFieldByLabel(client, "Текущий пароль", currentPassword), true);
    assert.equal(await setFieldByLabel(client, "Новый пароль", newPassword), true);
    assert.equal(await setFieldByLabel(client, "Повторите новый пароль", newPassword), true);
    assert.equal(await clickButton(client, "Изменить пароль"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Пароль изменён. Другие активные сессии завершены.")`,
      "password changed",
    );
    const passwordRequest = accountRequests.find(
      (item) => item.method === "POST" && item.path === "/api/v1/account/password",
    );
    assert.equal(passwordRequest?.body.current_password, currentPassword);
    assert.equal(passwordRequest?.body.new_password, newPassword);

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
      path.join(artifactDir, "account-profile-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );

    assert.equal(await clickButton(client, "Выйти"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Вход после выхода")`,
      "logout from personal account",
    );
    assert.ok(
      accountRequests.some(
        (item) => item.method === "POST" && item.path === "/api/v1/auth/logout",
      ),
    );

    client.close();
    console.log("Account profile browser acceptance passed.");
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
    path.join(artifactDir, "account-profile-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
