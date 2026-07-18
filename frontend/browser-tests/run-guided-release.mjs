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
const apiPort = 18085;
const debuggingPort = 9227;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const fixtureUrl = `${baseUrl}/browser-tests/guided-release.html`;
const chromeProfileDir = path.join("/tmp", "tourhub-guided-release-browser-profile");

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
  let project = null;
  let mealPlan = null;
  let preparation = null;
  const server = createServer((request, response) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => {
      const rawBody = Buffer.concat(chunks).toString("utf8");
      const body = rawBody ? JSON.parse(rawBody) : null;
      const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
      requests.push({ method: request.method ?? "GET", path: url.pathname, body });

      const sendJson = (status, payload) => {
        response.writeHead(status, { "content-type": "application/json" });
        response.end(JSON.stringify(payload));
      };

      if (request.method === "POST" && url.pathname === "/api/v1/projects") {
        project = {
          id: 77,
          ...body,
          start_date: body.start_date ?? null,
          recipe_generation_mode: body.recipe_generation_mode ?? "club_only",
          status: "draft",
        };
        sendJson(201, project);
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77") {
        sendJson(200, project);
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77/preparation") {
        if (!preparation) {
          sendJson(404, { error: "Project preparation not found" });
        } else {
          sendJson(200, preparation);
        }
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/meal-plans/project/77") {
        if (!mealPlan) {
          sendJson(404, { error: "Meal plan not found" });
        } else {
          sendJson(200, mealPlan);
        }
        return;
      }
      if (request.method === "POST" && url.pathname === "/api/v1/meal-plans/project/77/generate") {
        mealPlan = {
          id: "meal-plan-77",
          project_id: 77,
          name: "Карелия 2026",
          participants: 8,
          days_count: 3,
          items: [],
          meals: [],
          warnings: [],
        };
        sendJson(201, mealPlan);
        return;
      }
      if (request.method === "POST" && url.pathname === "/api/v1/projects/77/prepare") {
        preparation = {
          project_id: 77,
          meal_plan_id: "meal-plan-77",
          purchase_list_id: "purchase-list-77",
          purchase_checklist_id: "checklist-77",
          equipment_list_id: "equipment-77",
        };
        sendJson(201, preparation);
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77/preparation/status") {
        sendJson(200, {
          project_id: 77,
          readiness: {
            meal_plan: "ready",
            purchase_list: "ready",
            purchase_checklist: "ready",
            equipment_list: "ready",
            documents: "ready",
          },
          next_action: "documents",
        });
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77/purchase-list") {
        sendJson(200, { id: "purchase-list-77", items: [] });
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77/purchase-checklist") {
        sendJson(200, { id: "checklist-77", items: [], responsible_person: null });
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/projects/77/equipment-list") {
        sendJson(200, { id: "equipment-77", items: [], status: "prepared" });
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/documents/projects/77") {
        sendJson(200, { documents: [] });
        return;
      }
      if (request.method === "GET" && url.pathname === "/api/v1/auth/me") {
        sendJson(200, {
          id: 1,
          email: "admin@test.local",
          display_name: "Administrator",
          role: "administrator",
          is_active: true,
          version: 1,
        });
        return;
      }
      sendJson(404, { error: `Unhandled mock path: ${url.pathname}` });
    });
  });

  return {
    requests,
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

async function clickButton(client, text) {
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

async function setInput(client, selector, value) {
  const updated = await client.evaluate(`(() => {
    const input = document.querySelector(${JSON.stringify(selector)});
    if (!input) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, ${JSON.stringify(value)});
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  })()`);
  assert.equal(updated, true, `Input not found: ${selector}`);
}

async function setNumberInput(client, index, value) {
  const updated = await client.evaluate(`(() => {
    const input = document.querySelectorAll('input[type="number"]')[${index}];
    if (!input) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, ${JSON.stringify(value)});
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  })()`);
  assert.equal(updated, true, `Number input not found at index ${index}`);
}

async function waitForRequest(requests, method, requestPath, timeoutMs = 5_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const matches = requests.filter(
      (candidate) => candidate.method === method && candidate.path === requestPath,
    );
    if (matches.length > 0) return matches;
    await sleep(50);
  }
  assert.fail(`Request not observed: ${method} ${requestPath}`);
}

async function run() {
  await rm(chromeProfileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const errorPath = path.join(artifactDir, "guided-release-error.txt");
  await rm(errorPath, { force: true });

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
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
    });

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Создание похода")`,
      "project creation page",
    );
    await setInput(
      client,
      'input[placeholder="Например: Карелия 2026"]',
      "Карелия 2026",
    );
    await setNumberInput(client, 0, "8");
    await setNumberInput(client, 1, "3");
    await clickButton(client, "Создать поход");

    await waitForExpression(
      client,
      `location.pathname === "/projects/77" &&
       document.body?.innerText?.includes("Сформируйте меню для этого похода")`,
      "new project workspace",
    );
    const initialText = await client.evaluate("document.body.innerText");
    assert.ok(!initialText.includes("Не удалось загрузить список закупки"));

    const createRequests = await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/projects",
    );
    assert.deepEqual(createRequests[0].body, {
      name: "Карелия 2026",
      participants: 8,
      days: 3,
      first_meal: "dinner",
      last_meal: "dinner",
      recipe_generation_mode: "club_only",
    });

    await clickButton(client, "Сформировать меню");
    await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/meal-plans/project/77/generate",
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Рассчитайте закупку, создайте чек-лист и список оборудования")`,
      "preparation action",
    );

    await clickButton(client, "Подготовить проект");
    await waitForRequest(
      mockApi.requests,
      "POST",
      "/api/v1/projects/77/prepare",
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Документы готовы")`,
      "documents-ready state",
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 390,
      height: 844,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await client.evaluate("new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))");
    const layout = await client.evaluate(`(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    }))()`);
    assert.ok(
      layout.scrollWidth <= layout.clientWidth + 1 && layout.bodyScrollWidth <= layout.clientWidth + 1,
      `Horizontal overflow: ${JSON.stringify(layout)}`,
    );

    client.close();
  } catch (error) {
    await writeFile(errorPath, `${error.stack ?? error}\n`);
    throw error;
  } finally {
    await cleanup();
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
