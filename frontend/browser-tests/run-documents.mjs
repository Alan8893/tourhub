import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5180;
const apiPort = 18082;
const debuggingPort = 9232;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const pageUrl = `${baseUrl}/browser-tests/documents.html`;
const chromeProfileDir = path.join("/tmp", "tourhub-documents-profile");
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

async function waitForPageTarget(timeoutMs = 15_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then(
      (response) => response.json(),
    );
    const target = targets.find(
      (candidate) => candidate.type === "page" && candidate.url.includes("documents.html"),
    );
    if (target?.webSocketDebuggerUrl) return target;
    await sleep(100);
  }
  throw new Error("Chrome documents page target was not found");
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

function startMockApi() {
  const requests = [];
  const routes = new Map([
    ["/api/v1/projects/76/documents/purchase/pdf", "application/pdf"],
    [
      "/api/v1/projects/76/documents/purchase/excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    ["/api/v1/projects/76/documents/equipment/pdf", "application/pdf"],
    [
      "/api/v1/projects/76/documents/equipment/excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    ["/api/v1/projects/76/documents/package", "application/zip"],
  ]);

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    requests.push({ method: request.method ?? "GET", path: url.pathname });
    const contentType = routes.get(url.pathname);
    if (request.method === "GET" && contentType) {
      response.statusCode = 200;
      response.setHeader("content-type", contentType);
      response.end(Buffer.from(`document:${url.pathname}`));
      return;
    }
    response.statusCode = 404;
    response.setHeader("content-type", "application/json");
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
      throw new Error(
        result.exceptionDetails.exception?.description ??
          result.exceptionDetails.text ??
          "Browser evaluation failed",
      );
    }
    return result.result?.value;
  }

  close() {
    this.socket.close();
  }
}

async function waitForExpression(client, expression, description, timeoutMs = 15_000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      if (await client.evaluate(`Boolean(${expression})`)) return;
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  const snapshot = await client.evaluate(`(() => ({
    href: location.href,
    title: document.title,
    text: document.body?.innerText ?? "",
    root: document.getElementById("root")?.innerHTML ?? "",
  }))()`);
  throw new Error(
    `Timed out waiting for ${description}. ${lastError ?? ""} Snapshot: ${JSON.stringify(snapshot)}`,
  );
}

async function waitForRequest(requests, requestPath, timeoutMs = 5_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (
      requests.some(
        (request) => request.method === "GET" && request.path === requestPath,
      )
    ) {
      return;
    }
    await sleep(50);
  }
  assert.fail(`Request not observed: ${requestPath}`);
}

async function clickButton(client, label) {
  await waitForExpression(
    client,
    `(() => {
      const button = [...document.querySelectorAll("button")].find(
        (candidate) => candidate.textContent.trim() === ${JSON.stringify(label)},
      );
      return Boolean(button && !button.disabled);
    })()`,
    `${label} button`,
  );
  const clicked = await client.evaluate(`(() => {
    const button = [...document.querySelectorAll("button")].find(
      (candidate) => candidate.textContent.trim() === ${JSON.stringify(label)},
    );
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Could not click ${label}`);
}

async function stopProcess(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  child.kill("SIGKILL");
  await Promise.race([
    new Promise((resolve) => child.once("exit", resolve)),
    sleep(2_000),
  ]);
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

  await waitForHttp(pageUrl);
  const chrome = spawn(
    findChromeExecutable(),
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      `--remote-debugging-port=${debuggingPort}`,
      `--user-data-dir=${chromeProfileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  const cleanup = async () => {
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await mockApi.close();
    await rm(chromeProfileDir, { recursive: true, force: true });
  };

  try {
    await waitForHttp(`http://127.0.0.1:${debuggingPort}/json/version`);
    const pageTarget = await waitForPageTarget();
    const client = await CdpClient.connect(pageTarget.webSocketDebuggerUrl);
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
      `document.body?.innerText?.includes("Русские документы закупки и оборудования готовы") &&
       document.body.innerText.includes("Закупка PDF") &&
       document.body.innerText.includes("Закупка Excel") &&
       document.body.innerText.includes("Оборудование PDF") &&
       document.body.innerText.includes("Оборудование Excel") &&
       document.body.innerText.includes("Скачать полный пакет")`,
      "document download controls",
    );

    const actions = [
      ["Закупка PDF", "/api/v1/projects/76/documents/purchase/pdf"],
      ["Закупка Excel", "/api/v1/projects/76/documents/purchase/excel"],
      ["Оборудование PDF", "/api/v1/projects/76/documents/equipment/pdf"],
      ["Оборудование Excel", "/api/v1/projects/76/documents/equipment/excel"],
      ["Скачать полный пакет", "/api/v1/projects/76/documents/package"],
    ];
    for (const [label, requestPath] of actions) {
      await clickButton(client, label);
      await waitForRequest(mockApi.requests, requestPath);
    }

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
      path.join(artifactDir, "documents-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Documents browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "documents-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
