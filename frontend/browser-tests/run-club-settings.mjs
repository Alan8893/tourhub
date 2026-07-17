import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
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

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5181/browser-tests/club-settings.html";
const profileDir = "/tmp/tourhub-club-settings-profile";
const requests = [];

function createSettings() {
  return {
    version: 1,
    club_name: "Турклуб Север",
    short_name: "Север",
    legal_name: null,
    description: null,
    address: null,
    phone: null,
    email: null,
    website: null,
    timezone: null,
    city: null,
    region: null,
    social_links: [],
    images: {
      main_logo_data_url: null,
      light_logo_data_url: null,
      dark_logo_data_url: null,
      square_icon_data_url: null,
      favicon_data_url: null,
      login_background_data_url: null,
      document_image_data_url: null,
    },
    updated_at: "2026-07-17T12:00:00",
  };
}

function createMailSettings() {
  return {
    version: 1,
    smtp_host: "localhost",
    smtp_port: 587,
    security_mode: "starttls",
    smtp_username: null,
    sender_email: "tourhub@localhost",
    sender_name: "TourHub",
    reply_to_email: null,
    test_recipient_email: null,
    timeout_seconds: 30,
    retry_count: 3,
    updated_at: "2026-07-17T12:00:00",
    secret_configured: false,
    secret_source: "environment",
    secret_environment_variable: "TOURHUB_SMTP_SECRET",
    delivery_available: false,
    test_delivery_available: false,
  };
}

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function startApi() {
  let settings = createSettings();
  let history = [];
  const mailSettings = createMailSettings();
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (url.pathname === "/api/v1/settings/club") {
      if (request.method === "PUT") {
        if (body.expected_version !== settings.version) {
          response.statusCode = 409;
          response.end(JSON.stringify({ detail: "stale settings version" }));
          return;
        }
        settings = {
          ...settings,
          ...body,
          version: settings.version + 1,
          images: settings.images,
          updated_at: "2026-07-17T12:05:00",
        };
        delete settings.expected_version;
        history = [
          {
            id: 1,
            section: "club",
            actor_label: "Локальный администратор",
            action: "updated",
            changed_fields: ["club_name"],
            settings_version: settings.version,
            created_at: "2026-07-17T12:05:00",
          },
        ];
      }
      response.statusCode = 200;
      response.end(JSON.stringify(settings));
      return;
    }

    if (url.pathname === "/api/v1/settings/history") {
      response.statusCode = 200;
      response.end(JSON.stringify(history));
      return;
    }

    if (url.pathname === "/api/v1/settings/mail") {
      response.statusCode = 200;
      response.end(JSON.stringify(mailSettings));
      return;
    }

    if (url.pathname === "/api/v1/settings/mail/history") {
      response.statusCode = 200;
      response.end(JSON.stringify([]));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ detail: "not found" }));
  });
  return {
    listen: () => new Promise((resolve) => server.listen(18083, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5181",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18083" },
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
      "--remote-debugging-port=9233",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9233/json/version");
    const targets = await fetch("http://127.0.0.1:9233/json/list").then((r) => r.json());
    const target = targets.find((item) => item.url.includes("club-settings.html"));
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
    await sleep(200);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки") &&
       document.body?.innerText?.includes("Клуб") &&
       [...document.querySelectorAll('input')].some((item) => item.value === "Турклуб Север")`,
      "loaded system settings",
    );

    assert.equal(
      await client.evaluate(`(() => {
        const input = [...document.querySelectorAll('input')].find(
          (item) => item.value === "Турклуб Север",
        );
        if (!input) return false;
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        setter.call(input, "Турклуб Полюс");
        input.dispatchEvent(new Event("input", { bubbles: true }));
        return true;
      })()`),
      true,
    );

    assert.equal(
      await client.evaluate(`(() => {
        const button = [...document.querySelectorAll("button")].find(
          (item) => item.textContent.trim() === "Сохранить раздел",
        );
        if (!button || button.disabled) return false;
        button.click();
        return true;
      })()`),
      true,
    );

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки клуба сохранены") &&
       document.body?.innerText?.includes("Локальный администратор")`,
      "saved club settings and history",
    );

    const put = requests.find((item) => item.method === "PUT");
    assert.equal(put?.path, "/api/v1/settings/club");
    assert.equal(put?.body.expected_version, 1);
    assert.equal(put?.body.club_name, "Турклуб Полюс");
    assert.deepEqual(put?.body.images, {});

    assert.equal(
      await client.evaluate(`(() => {
        const button = [...document.querySelectorAll("div[role='button'], button")].find(
          (item) => item.textContent?.trim().startsWith("Почта"),
        );
        if (!button) return false;
        button.click();
        return true;
      })()`),
      true,
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("TOURHUB_SMTP_SECRET") &&
       document.body?.innerText?.includes("TourHub пока не") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Отправить тестовое письмо" && item.disabled,
       )`,
      "working mail boundary section",
    );
    assert.equal(await client.evaluate(`document.querySelector('input[type="password"]')`), null);

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(350);
    const layout = await client.evaluate(`(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
      hasSectionSelect: [...document.querySelectorAll('[role="combobox"]')].some(
        (item) => item.textContent?.includes("Почта"),
      ),
    }))()`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 &&
        layout.bodyScrollWidth <= layout.clientWidth + 1,
    );
    assert.equal(layout.hasSectionSelect, true);

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "club-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("System settings browser acceptance passed.");
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
    path.join(artifactDir, "club-settings-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
