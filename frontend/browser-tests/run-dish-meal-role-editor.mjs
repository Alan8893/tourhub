import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5173;
const apiPort = 18081;
const debuggingPort = 9223;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const fixtureUrl = `${baseUrl}/browser-tests/dish-meal-role-editor.html`;
const chromeProfileDir = path.join("/tmp", "tourhub-dish-role-browser-profile");

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function waitForHttp(url, timeoutMs = 30_000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;

  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
      lastError = new Error(`${url} returned ${response.status}`);
    } catch (error) {
      lastError = error;
    }
    await sleep(250);
  }

  throw lastError ?? new Error(`Timed out waiting for ${url}`);
}

function findChromeExecutable() {
  const candidates = [
    process.env.CHROME_BIN,
    "/usr/bin/google-chrome-stable",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ].filter(Boolean);

  const executable = candidates.find((candidate) => existsSync(candidate));
  if (!executable) {
    throw new Error("Chrome or Chromium was not found. Set CHROME_BIN to a browser executable.");
  }
  return executable;
}

function startMockApi() {
  const requests = [];
  let failNextRoleMutation = false;
  let dish = {
    id: "dish-soup",
    name: "Суп походный",
    recipe: { id: "recipe-soup", name: "Суп базовый", is_archived: false },
    meal_roles: [],
  };

  const server = createServer((request, response) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => {
      const body = Buffer.concat(chunks).toString("utf8");
      const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
      requests.push({ method: request.method ?? "GET", path: url.pathname, body });

      const sendJson = (status, payload) => {
        response.writeHead(status, { "content-type": "application/json" });
        response.end(JSON.stringify(payload));
      };

      if (request.method === "GET" && url.pathname === "/api/v1/dishes") {
        sendJson(200, { items: [dish] });
        return;
      }

      if (request.method === "GET" && url.pathname === "/api/v1/dishes/dish-soup") {
        sendJson(200, dish);
        return;
      }

      if (request.method === "GET" && url.pathname === "/api/v1/recipes") {
        sendJson(200, {
          items: [
            {
              id: "recipe-soup",
              name: "Суп базовый",
              component_count: 1,
              note_count: 0,
              is_archived: false,
            },
          ],
        });
        return;
      }

      if (request.method === "PUT" && url.pathname === "/api/v1/dishes/dish-soup/meal-roles") {
        if (failNextRoleMutation) {
          failNextRoleMutation = false;
          sendJson(500, { error: "Проверочная ошибка сохранения ролей." });
          return;
        }

        const payload = JSON.parse(body);
        dish = { ...dish, meal_roles: payload.roles };
        sendJson(200, dish);
        return;
      }

      sendJson(404, { error: `Unhandled mock path: ${url.pathname}` });
    });
  });

  return {
    requests,
    failNextRoleMutation: () => {
      failNextRoleMutation = true;
    },
    listen: () => new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(apiPort, "127.0.0.1", resolve);
    }),
    close: () => new Promise((resolve) => {
      server.closeAllConnections();
      server.close(resolve);
    }),
  };
}

class CdpClient {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();

    socket.addEventListener("message", (event) => {
      const message = JSON.parse(String(event.data));
      if (!message.id) return;
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) pending.reject(new Error(message.error.message));
      else pending.resolve(message.result ?? {});
    });
  }

  static async connect(url) {
    const socket = new WebSocket(url);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", reject, { once: true });
    });
    return new CdpClient(socket);
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (result.exceptionDetails) {
      throw new Error(result.exceptionDetails.text ?? "Browser evaluation failed");
    }
    return result.result?.value;
  }

  close() {
    this.socket.close();
  }
}

async function waitForExpression(client, expression, description, timeoutMs = 10_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await client.evaluate(`Boolean(${expression})`)) return;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function waitForStableCataloguePage(client, description) {
  await waitForExpression(
    client,
    `(() => {
      const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
      const createButton = Array.from(document.querySelectorAll("button"))
        .find((button) => normalize(button.textContent) === "Создать блюдо");
      return !document.querySelector('[role="dialog"]') && Boolean(createButton && !createButton.disabled);
    })()`,
    description,
  );
}

async function clickButtonByText(client, text) {
  const clicked = await client.evaluate(`(() => {
    const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
    const button = Array.from(document.querySelectorAll("button"))
      .find((candidate) => normalize(candidate.textContent) === ${JSON.stringify(text)} && !candidate.disabled);
    if (!button) return false;
    button.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Button not found or disabled: ${text}`);
}

async function clickCheckboxByAriaLabel(client, label) {
  const clicked = await client.evaluate(`(() => {
    const input = document.querySelector(${JSON.stringify(`input[aria-label="${label}"]`)});
    if (!input || input.disabled) return false;
    input.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Checkbox not found or disabled: ${label}`);
}

async function waitForRequest(requests, method, requestPath, timeoutMs = 5_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const request = requests.findLast(
      (candidate) => candidate.method === method && candidate.path === requestPath,
    );
    if (request) return request;
    await sleep(50);
  }
  assert.fail(`Request not observed: ${method} ${requestPath}`);
}

async function setViewport(client, width, height) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 480,
  });
}

async function assertNoHorizontalOverflow(client, width) {
  const layout = await client.evaluate(`(() => ({
    innerWidth: window.innerWidth,
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
  }))()`);
  assert.ok(
    layout.scrollWidth <= layout.clientWidth + 1 && layout.bodyScrollWidth <= layout.clientWidth + 1,
    `Horizontal overflow at ${width}px: ${JSON.stringify(layout)}`,
  );
}

async function captureScreenshot(client, name) {
  const screenshot = await client.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  await writeFile(path.join(artifactDir, `${name}.png`), Buffer.from(screenshot.data, "base64"));
}

async function resizeAndCapture(client, width, height, name) {
  await setViewport(client, width, height);
  await client.evaluate("new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))");
  await waitForExpression(
    client,
    `document.body.innerText.includes("Суп походный")
      && document.body.innerText.includes("Основное: обед")
      && document.body.innerText.includes("Напиток: завтрак, обед, ужин · можно повторять")`,
    `classified dish render at ${width}px`,
  );
  await waitForStableCataloguePage(client, `stable catalogue page at ${width}px`);
  await assertNoHorizontalOverflow(client, width);
  await captureScreenshot(client, name);
}

async function run() {
  await rm(chromeProfileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });

  const mockApi = startMockApi();
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

  const chrome = spawn(findChromeExecutable(), [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    `--remote-debugging-port=${debuggingPort}`,
    `--user-data-dir=${chromeProfileDir}`,
    "about:blank",
  ], { stdio: "ignore" });

  const cleanup = async () => {
    chrome.kill("SIGKILL");
    vite.kill("SIGKILL");
    await mockApi.close();
  };

  try {
    await waitForHttp(fixtureUrl);
    await waitForHttp(`http://127.0.0.1:${debuggingPort}/json/version`);

    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then((response) => response.json());
    const pageTarget = targets.find((target) => target.type === "page");
    assert.ok(pageTarget?.webSocketDebuggerUrl, "Chrome page target was not found");

    const client = await CdpClient.connect(pageTarget.webSocketDebuggerUrl);
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await setViewport(client, 1280, 900);
    await client.send("Page.navigate", { url: fixtureUrl });

    await waitForExpression(
      client,
      `document.readyState === "complete"
        && document.body.innerText.includes("Суп походный")
        && document.body.innerText.includes("Роли не назначены")`,
      "unclassified dish render",
    );
    await waitForStableCataloguePage(client, "stable unclassified dish page");

    await clickButtonByText(client, "Настроить роли");
    await waitForExpression(
      client,
      `document.body.innerText.includes("Роли блюда «Суп походный»")`,
      "role editor dialog",
    );
    await clickCheckboxByAriaLabel(client, "Назначить роль «Основное блюдо»");
    await clickButtonByText(client, "Сохранить роли");
    await waitForExpression(
      client,
      `Array.from(document.querySelectorAll('[role="alert"]'))
        .some((alert) => alert.textContent?.includes("Выберите хотя бы один приём пищи для роли «Основное блюдо»."))`,
      "local meal type validation",
    );

    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Основное блюдо» для приёма пищи «Обед»",
    );
    await clickCheckboxByAriaLabel(client, "Назначить роль «Напиток»");
    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Напиток» для приёма пищи «Завтрак»",
    );
    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Напиток» для приёма пищи «Обед»",
    );
    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Напиток» для приёма пищи «Ужин»",
    );
    await clickCheckboxByAriaLabel(client, "Разрешить повторение роли «Напиток»");
    await clickButtonByText(client, "Сохранить роли");

    await waitForExpression(
      client,
      `document.body.innerText.includes("Роли блюда сохранены.")
        && document.body.innerText.includes("Основное: обед")
        && document.body.innerText.includes("Напиток: завтрак, обед, ужин · можно повторять")`,
      "saved role and meal type feedback",
    );
    await waitForStableCataloguePage(client, "closed role dialog after save");

    const request = await waitForRequest(
      mockApi.requests,
      "PUT",
      "/api/v1/dishes/dish-soup/meal-roles",
    );
    assert.deepEqual(JSON.parse(request.body), {
      roles: [
        {
          role: "main",
          is_repeatable: false,
          allowed_meal_types: ["lunch"],
        },
        {
          role: "drink",
          is_repeatable: true,
          allowed_meal_types: ["breakfast", "lunch", "dinner"],
        },
      ],
    });

    await assertNoHorizontalOverflow(client, 1280);
    await captureScreenshot(client, "dish-meal-role-editor-desktop");

    await clickButtonByText(client, "Настроить роли");
    await clickCheckboxByAriaLabel(client, "Назначить роль «Перекус»");
    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Перекус» для приёма пищи «Перекус»",
    );
    mockApi.failNextRoleMutation();
    await clickButtonByText(client, "Сохранить роли");
    await waitForExpression(
      client,
      `Array.from(document.querySelectorAll('[role="alert"]'))
        .some((alert) => alert.textContent?.includes("Проверочная ошибка сохранения ролей."))`,
      "role mutation error feedback",
    );
    await clickButtonByText(client, "Отмена");
    await waitForStableCataloguePage(client, "closed role dialog after error");

    await resizeAndCapture(client, 768, 900, "dish-meal-role-editor-tablet");
    await resizeAndCapture(client, 360, 800, "dish-meal-role-editor-mobile");

    client.close();
    console.log("Dish Meal Role Editor browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "dish-meal-role-browser-acceptance-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
