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
const debuggingPort = 9228;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const chromeProfileDir = path.join("/tmp", "tourhub-equipment-list-profile");
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
  if (!executable) throw new Error("Chrome or Chromium was not found");
  return executable;
}

async function readJsonBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const text = Buffer.concat(chunks).toString("utf8");
  return text ? JSON.parse(text) : undefined;
}

function startMockApi() {
  const requests = [];
  const equipmentList = {
    id: "73000000-0000-0000-0000-000000000002",
    project_id: 73,
    meal_plan_id: "73000000-0000-0000-0000-000000000001",
    status: "prepared",
    items: [
      {
        id: "73000000-0000-0000-0000-000000000003",
        equipment_name: "Котёл",
        required_quantity: 3,
        calculated_quantity: 3,
        is_manual: false,
        is_overridden: false,
      },
      {
        id: "73000000-0000-0000-0000-000000000004",
        equipment_name: "Горелка",
        required_quantity: 2,
        calculated_quantity: 2,
        is_manual: false,
        is_overridden: false,
      },
    ],
  };

  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "GET" ? undefined : await readJsonBody(request);
    requests.push({ method: request.method ?? "GET", path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (
      request.method === "GET" &&
      url.pathname === "/api/v1/equipment-lists/project/73"
    ) {
      response.statusCode = 200;
      response.end(JSON.stringify(equipmentList));
      return;
    }

    if (
      request.method === "POST" &&
      url.pathname === "/api/v1/equipment-lists/project/73/items"
    ) {
      const item = {
        id: "73000000-0000-0000-0000-000000000005",
        equipment_name: body.equipment_name,
        required_quantity: body.required_quantity,
        calculated_quantity: null,
        is_manual: true,
        is_overridden: false,
      };
      equipmentList.items.push(item);
      response.statusCode = 201;
      response.end(JSON.stringify(item));
      return;
    }

    const itemMatch = url.pathname.match(
      /^\/api\/v1\/equipment-lists\/project\/73\/items\/([^/]+)$/,
    );
    if (itemMatch && request.method === "PUT") {
      const item = equipmentList.items.find((candidate) => candidate.id === itemMatch[1]);
      assert.ok(item, "Equipment item for PUT was not found");
      item.required_quantity = body.required_quantity;
      item.is_overridden =
        item.calculated_quantity !== null &&
        item.required_quantity !== item.calculated_quantity;
      response.statusCode = 200;
      response.end(JSON.stringify(item));
      return;
    }

    if (itemMatch && request.method === "DELETE") {
      const index = equipmentList.items.findIndex((candidate) => candidate.id === itemMatch[1]);
      assert.notEqual(index, -1, "Equipment item for DELETE was not found");
      equipmentList.items.splice(index, 1);
      response.statusCode = 204;
      response.end();
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ detail: `Unhandled mock path: ${url.pathname}` }));
  });

  return {
    requests,
    listen: () =>
      new Promise((resolve, reject) => {
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

async function waitForRequest(requests, predicate, description, timeoutMs = 5_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const match = requests.find(predicate);
    if (match) return match;
    await sleep(50);
  }
  assert.fail(`Request not observed: ${description}`);
}

function setInputExpression(label, value) {
  return `(() => {
    const input = document.querySelector('input[aria-label="${label}"]');
    if (!input) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, ${JSON.stringify(value)});
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  })()`;
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

  const chrome = spawn(
    findChromeExecutable(),
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      `--remote-debugging-port=${debuggingPort}`,
      `--user-data-dir=${chromeProfileDir}`,
      "about:blank",
    ],
    { stdio: "ignore" },
  );

  const cleanup = async () => {
    chrome.kill("SIGKILL");
    vite.kill("SIGKILL");
    await mockApi.close();
    await rm(chromeProfileDir, { recursive: true, force: true });
  };

  try {
    await waitForHttp(`${baseUrl}/browser-tests/equipment-list.html`);
    await waitForHttp(`http://127.0.0.1:${debuggingPort}/json/version`);
    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then(
      (response) => response.json(),
    );
    const pageTarget = targets.find((target) => target.type === "page");
    assert.ok(pageTarget?.webSocketDebuggerUrl, "Chrome page target was not found");

    const client = await CdpClient.connect(pageTarget.webSocketDebuggerUrl);
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 900,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await client.send("Page.navigate", {
      url: `${baseUrl}/browser-tests/equipment-list.html`,
    });

    await waitForExpression(
      client,
      `document.body.innerText.includes("Оборудование") &&
       document.body.innerText.includes("Итоговый список можно изменить вручную") &&
       document.body.innerText.includes("Позиций: 2 · Всего единиц: 5") &&
       document.body.innerText.includes("Котёл") &&
       document.body.innerText.includes("Расчёт 3") &&
       document.body.innerText.includes("Горелка")`,
      "initial persisted equipment list",
    );

    assert.equal(await client.evaluate(setInputExpression("Количество: Котёл", "5")), true);
    await client.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")].find(
        (candidate) => candidate.textContent.trim() === "Сохранить" && !candidate.disabled,
      );
      if (!button) return false;
      button.click();
      return true;
    })()`);
    await waitForRequest(
      mockApi.requests,
      (request) =>
        request.method === "PUT" &&
        request.path.endsWith("73000000-0000-0000-0000-000000000003") &&
        request.body?.required_quantity === 5,
      "equipment quantity override PUT",
    );
    await waitForExpression(
      client,
      `document.body.innerText.includes("Изменено · расчёт 3") &&
       document.body.innerText.includes("Позиций: 2 · Всего единиц: 7")`,
      "saved equipment override",
    );

    assert.equal(
      await client.evaluate(setInputExpression("Новое оборудование проекта", "Фонарь")),
      true,
    );
    assert.equal(
      await client.evaluate(
        setInputExpression("Количество нового оборудования проекта", "2"),
      ),
      true,
    );
    await client.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")].find(
        (candidate) => candidate.textContent.trim() === "Добавить" && !candidate.disabled,
      );
      if (!button) return false;
      button.click();
      return true;
    })()`);
    await waitForRequest(
      mockApi.requests,
      (request) =>
        request.method === "POST" &&
        request.path === "/api/v1/equipment-lists/project/73/items" &&
        request.body?.equipment_name === "Фонарь" &&
        request.body?.required_quantity === 2,
      "manual equipment POST",
    );
    await waitForExpression(
      client,
      `document.body.innerText.includes("Фонарь") &&
       document.body.innerText.includes("Добавлено вручную") &&
       document.body.innerText.includes("Позиций: 3 · Всего единиц: 9")`,
      "manual equipment item",
    );

    await client.evaluate(`(() => {
      window.confirm = () => true;
      const input = document.querySelector('input[aria-label="Количество: Горелка"]');
      let node = input;
      while (node && !(
        node.innerText?.includes("Горелка") &&
        [...node.querySelectorAll("button")].some(
          (button) => button.textContent.trim() === "Удалить"
        )
      )) node = node.parentElement;
      const button = node && [...node.querySelectorAll("button")].find(
        (candidate) => candidate.textContent.trim() === "Удалить"
      );
      if (!button) return false;
      button.click();
      return true;
    })()`);
    await waitForRequest(
      mockApi.requests,
      (request) =>
        request.method === "DELETE" &&
        request.path.endsWith("73000000-0000-0000-0000-000000000004"),
      "equipment removal DELETE",
    );
    await waitForExpression(
      client,
      `!document.body.innerText.includes("Горелка") &&
       document.body.innerText.includes("Позиций: 2 · Всего единиц: 7")`,
      "removed calculated equipment item",
    );

    assert.ok(
      mockApi.requests.filter(
        (request) =>
          request.method === "GET" &&
          request.path === "/api/v1/equipment-lists/project/73",
      ).length >= 4,
      "Expected equipment refetch after each mutation",
    );

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(250);
    const layout = await client.evaluate(`(() => ({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    }))()`);
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
      path.join(artifactDir, "equipment-list-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );

    client.close();
    console.log("Equipment list override browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "equipment-list-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
