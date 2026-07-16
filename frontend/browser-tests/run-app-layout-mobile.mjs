import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5176;
const debuggingPort = 9226;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const fixtureUrl = `${baseUrl}/browser-tests/app-layout-mobile.html`;
const chromeProfileDir = path.join("/tmp", `tourhub-mobile-navigation-${process.pid}`);

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
  if (!executable) throw new Error("Chrome or Chromium was not found.");
  return executable;
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
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? "Browser evaluation failed");
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

async function setViewport(client, width, height) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 480,
  });
  await client.evaluate("new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))");
}

async function clickByAriaLabel(client, label) {
  const clicked = await client.evaluate(`(() => {
    const element = document.querySelector(${JSON.stringify(`[aria-label="${label}"]`)});
    if (!element) return false;
    element.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Element not found: ${label}`);
}

async function clickVisibleLinkByText(client, text) {
  const clicked = await client.evaluate(`(() => {
    const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
    const link = Array.from(document.querySelectorAll("a")).find((candidate) => {
      const rect = candidate.getBoundingClientRect();
      const style = getComputedStyle(candidate);
      return normalize(candidate.textContent) === ${JSON.stringify(text)}
        && rect.width > 0
        && rect.height > 0
        && style.visibility !== "hidden"
        && style.display !== "none";
    });
    if (!link) return false;
    link.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Visible navigation link not found: ${text}`);
}

async function visibleDrawerCount(client) {
  return client.evaluate(`Array.from(document.querySelectorAll(".MuiDrawer-paper")).filter((element) => {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none";
  }).length`);
}

async function assertNoHorizontalOverflow(client, width) {
  const layout = await client.evaluate(`(() => ({
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

async function run() {
  await rm(chromeProfileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });

  const vite = spawn(process.execPath, [
    path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
    "--host", "127.0.0.1", "--port", String(frontendPort), "--strictPort",
  ], { cwd: frontendRoot, stdio: "ignore" });
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
    await sleep(200);
    await rm(chromeProfileDir, { recursive: true, force: true }).catch(() => undefined);
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
    await setViewport(client, 360, 800);
    await client.send("Page.navigate", { url: fixtureUrl });

    await waitForExpression(
      client,
      `document.body.innerText.includes("Блюда мобильный тест")
        && document.querySelector('button[aria-label="Открыть меню"]')`,
      "closed mobile layout",
    );
    assert.equal(await visibleDrawerCount(client), 0, "Mobile drawer must be closed by default");

    const mobileContent = await client.evaluate(`(() => {
      const heading = document.querySelector("h1");
      if (!heading) return null;
      const rect = heading.getBoundingClientRect();
      return { left: rect.left, right: rect.right, viewport: window.innerWidth };
    })()`);
    assert.ok(mobileContent, "Mobile page heading was not found");
    assert.ok(mobileContent.left <= 20, `Mobile content starts too far right: ${JSON.stringify(mobileContent)}`);
    assert.ok(mobileContent.right <= mobileContent.viewport, `Mobile content exceeds viewport: ${JSON.stringify(mobileContent)}`);
    await assertNoHorizontalOverflow(client, 360);
    await captureScreenshot(client, "app-layout-mobile-closed");

    await clickByAriaLabel(client, "Открыть меню");
    await waitForExpression(client, `(async () => ${await visibleDrawerCount(client)} > 0)()`, "open mobile drawer").catch(async () => {
      await waitForExpression(
        client,
        `Array.from(document.querySelectorAll(".MuiDrawer-paper")).some((element) => element.getBoundingClientRect().width > 0 && getComputedStyle(element).visibility !== "hidden")`,
        "open mobile drawer",
      );
    });
    const drawerWidth = await client.evaluate(`Math.max(...Array.from(document.querySelectorAll(".MuiDrawer-paper")).map((element) => element.getBoundingClientRect().width))`);
    assert.ok(drawerWidth <= 281, `Mobile drawer is too wide: ${drawerWidth}px`);
    await captureScreenshot(client, "app-layout-mobile-open");

    await clickVisibleLinkByText(client, "Рецепты");
    await waitForExpression(client, `document.body.innerText.includes("Рецепты мобильный тест")`, "mobile route navigation");
    await waitForExpression(
      client,
      `!Array.from(document.querySelectorAll(".MuiDrawer-paper")).some((element) => element.getBoundingClientRect().width > 0 && getComputedStyle(element).visibility !== "hidden")`,
      "drawer close after navigation",
    );
    await captureScreenshot(client, "app-layout-mobile-after-navigation");

    await setViewport(client, 1280, 850);
    await waitForExpression(
      client,
      `getComputedStyle(document.querySelector('button[aria-label="Открыть меню"]')).display === "none"`,
      "desktop menu button hidden",
    );
    assert.equal(await visibleDrawerCount(client), 1, "Desktop must show exactly one permanent drawer");
    await assertNoHorizontalOverflow(client, 1280);
    await captureScreenshot(client, "app-layout-desktop");

    client.close();
    console.log("Responsive app navigation browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "app-layout-mobile-browser-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
