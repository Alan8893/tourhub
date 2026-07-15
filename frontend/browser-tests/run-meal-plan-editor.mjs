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
const apiPort = 18080;
const debuggingPort = 9222;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const chromeProfileDir = path.join("/tmp", "tourhub-browser-acceptance-profile");

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
  let failNextMutation = false;

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
        sendJson(200, {
          items: [
            { id: "dish-soup", name: "Суп", recipe: { id: "recipe-1", name: "Суп", is_archived: false } },
            { id: "dish-fruit", name: "Сухофрукты", recipe: { id: "recipe-2", name: "Сухофрукты", is_archived: false } },
          ],
        });
        return;
      }

      if (url.pathname.startsWith("/api/v1/meal-slots/")) {
        if (failNextMutation) {
          failNextMutation = false;
          sendJson(500, { detail: "Browser acceptance injected failure" });
          return;
        }

        const parts = url.pathname.split("/").filter(Boolean);
        const dishId = parts.at(-1) ?? "dish-unknown";
        sendJson(200, { id: "slot-dish-result", dish_id: dishId, status: "ok" });
        return;
      }

      sendJson(404, { detail: `Unhandled mock path: ${url.pathname}` });
    });
  });

  return {
    requests,
    failNextMutation: () => {
      failNextMutation = true;
    },
    listen: () => new Promise((resolve, reject) => {
      server.once("error", reject);
      server.listen(apiPort, "127.0.0.1", resolve);
    }),
    close: () =>
      new Promise((resolve) => {
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

async function clickButtonByAriaLabel(client, label) {
  const clicked = await client.evaluate(`(() => {
    const button = document.querySelector(${JSON.stringify(`button[aria-label="${label}"]`)});
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Button not found or disabled: ${label}`);
}

async function selectMuiOption(client, label, optionText) {
  await waitForExpression(
    client,
    `Array.from(document.querySelectorAll('[role="combobox"]')).some((candidate) => {
      const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
      const labelledBy = (candidate.getAttribute("aria-labelledby") ?? "").split(/\\s+/);
      const matchesLabel = labelledBy.some((id) =>
        normalize(document.getElementById(id)?.textContent) === ${JSON.stringify(label)}
      );
      return matchesLabel && candidate.getAttribute("aria-disabled") !== "true";
    })`,
    `enabled select ${label}`,
  );

  const opened = await client.evaluate(`(() => {
    const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
    const controls = Array.from(document.querySelectorAll('[role="combobox"]'));
    const control = controls.find((candidate) => {
      const labelledBy = (candidate.getAttribute("aria-labelledby") ?? "").split(/\\s+/);
      return labelledBy.some((id) => normalize(document.getElementById(id)?.textContent) === ${JSON.stringify(label)});
    });
    if (!control) return false;
    control.dispatchEvent(new MouseEvent("mousedown", { bubbles: true, cancelable: true, button: 0 }));
    return true;
  })()`);
  assert.equal(opened, true, `Select not found: ${label}`);

  await waitForExpression(
    client,
    `Array.from(document.querySelectorAll('[role="option"]')).some((option) => option.textContent?.trim() === ${JSON.stringify(optionText)})`,
    `option ${optionText}`,
  );

  const selected = await client.evaluate(`(() => {
    const option = Array.from(document.querySelectorAll('[role="option"]'))
      .find((candidate) => candidate.textContent?.trim() === ${JSON.stringify(optionText)});
    if (!option) return false;
    option.click();
    return true;
  })()`);
  assert.equal(selected, true, `Option not found: ${optionText}`);
}

async function waitForRequest(requests, method, requestPath, timeoutMs = 5_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (requests.some((request) => request.method === method && request.path === requestPath)) return;
    await sleep(50);
  }
  assert.fail(`Request not observed: ${method} ${requestPath}`);
}

async function captureViewport(client, width, height, name) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 480,
  });
  await client.send("Page.navigate", { url: `${baseUrl}/browser-tests/meal-plan-editor.html` });
  await waitForExpression(
    client,
    `document.readyState === "complete" && document.body.innerText.includes("Овсяная каша")`,
    `editor render at ${width}px`,
  );

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

  const screenshot = await client.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  await writeFile(path.join(artifactDir, `${name}.png`), Buffer.from(screenshot.data, "base64"));
}

async function run() {
  await rm(artifactDir, { recursive: true, force: true });
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
    await rm(chromeProfileDir, { recursive: true, force: true });
  };

  try {
    await waitForHttp(`${baseUrl}/browser-tests/meal-plan-editor.html`);
    await waitForHttp(`http://127.0.0.1:${debuggingPort}/json/version`);

    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then((response) => response.json());
    const pageTarget = targets.find((target) => target.type === "page");
    assert.ok(pageTarget?.webSocketDebuggerUrl, "Chrome page target was not found");

    const client = await CdpClient.connect(pageTarget.webSocketDebuggerUrl);
    await client.send("Page.enable");
    await client.send("Runtime.enable");

    await captureViewport(client, 1280, 900, "meal-plan-editor-desktop");

    await clickButtonByAriaLabel(client, "Заменить блюдо «Овсяная каша»");
    await selectMuiOption(client, "Новое блюдо", "Суп");
    await clickButtonByText(client, "Сохранить");
    await waitForExpression(client, `document.body.innerText.includes("Блюдо заменено.")`, "replace success feedback");
    await waitForRequest(
      mockApi.requests,
      "PUT",
      "/api/v1/meal-slots/slot-1/dishes/slot-dish-1/dish-soup",
    );

    await clickButtonByAriaLabel(client, "Удалить блюдо «Чай»");
    await waitForExpression(
      client,
      `document.body.innerText.includes("Удалить блюдо «Чай» из этого приёма пищи?")`,
      "remove confirmation",
    );
    await clickButtonByText(client, "Да, удалить");
    await waitForExpression(client, `document.body.innerText.includes("Блюдо удалено.")`, "remove success feedback");
    await waitForRequest(mockApi.requests, "DELETE", "/api/v1/meal-slots/slot-1/dishes/slot-dish-2");

    await clickButtonByText(client, "Добавить блюдо");
    await selectMuiOption(client, "Блюдо для добавления", "Сухофрукты");
    await clickButtonByText(client, "Добавить");
    await waitForExpression(client, `document.body.innerText.includes("Блюдо добавлено.")`, "add success feedback");
    await waitForRequest(mockApi.requests, "POST", "/api/v1/meal-slots/slot-1/dishes/dish-fruit");

    mockApi.failNextMutation();
    await clickButtonByText(client, "Добавить блюдо");
    await selectMuiOption(client, "Блюдо для добавления", "Суп");
    await clickButtonByText(client, "Добавить");
    await waitForExpression(
      client,
      `document.querySelector('[role="alert"]')?.textContent?.includes("Не удалось изменить состав приёма пищи")`,
      "mutation error feedback",
    );

    await captureViewport(client, 768, 900, "meal-plan-editor-tablet");
    await captureViewport(client, 360, 800, "meal-plan-editor-mobile");

    client.close();
    console.log("Meal Plan Editor browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "browser-acceptance-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
