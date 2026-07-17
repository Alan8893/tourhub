import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { requests, startAccessAuthApi } from "./access-auth-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5187/browser-tests/access-auth.html";
const profileDir = "/tmp/tourhub-access-auth-profile";

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startAccessAuthApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5187",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18089" },
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
      "--remote-debugging-port=9239",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9239/json/version");
    const targets = await fetch("http://127.0.0.1:9239/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("access-auth.html"));
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

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Создание первого администратора") &&
       document.body?.innerText?.includes("Создать администратора")`,
      "bootstrap form",
    );
    assert.equal(await setFieldByLabel(client, "Имя администратора", "Иван Администратор"), true);
    assert.equal(await setFieldByLabel(client, "Email", "Admin@TourHub.Local"), true);
    assert.equal(
      await setFieldByLabel(client, "Пароль", "correct-horse-battery-staple"),
      true,
    );
    assert.equal(
      await setFieldByLabel(client, "Повторите пароль", "correct-horse-battery-staple"),
      true,
    );
    assert.equal(await clickButton(client, "Создать администратора"), true);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки доступны") &&
       document.body?.innerText?.includes("Иван Администратор") &&
       document.body?.innerText?.includes("admin@tourhub.local") &&
       [...document.querySelectorAll("button")].some((item) => item.textContent?.trim() === "Выйти")`,
      "authenticated settings",
    );
    assert.equal(await client.evaluate("document.cookie.includes('tourhub_session')"), false);

    const bootstrapRequest = requests.find(
      (item) => item.method === "POST" && item.path === "/api/v1/auth/bootstrap",
    );
    assert.equal(bootstrapRequest?.body.display_name, "Иван Администратор");
    assert.equal(bootstrapRequest?.body.email, "Admin@TourHub.Local");

    assert.equal(await clickButton(client, "Выйти"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Вход") &&
       [...document.querySelectorAll("button")].some((item) => item.textContent?.trim() === "Войти")`,
      "login form after logout",
    );
    assert.equal(await setFieldByLabel(client, "Email", "admin@tourhub.local"), true);
    assert.equal(
      await setFieldByLabel(client, "Пароль", "correct-horse-battery-staple"),
      true,
    );
    assert.equal(await clickButton(client, "Войти"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки доступны") &&
       document.body?.innerText?.includes("Иван Администратор")`,
      "settings after login",
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 800,
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
      path.join(artifactDir, "access-auth-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Access bootstrap and login browser acceptance passed.");
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
    path.join(artifactDir, "access-auth-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
