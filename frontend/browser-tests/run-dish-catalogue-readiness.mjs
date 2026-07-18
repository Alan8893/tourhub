import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const frontendPort = 5174;
const apiPort = 18082;
const debuggingPort = 9224;
const baseUrl = `http://127.0.0.1:${frontendPort}`;
const fixtureUrl = `${baseUrl}/browser-tests/dish-meal-role-editor.html`;
const chromeProfileDir = path.join("/tmp", `tourhub-readiness-profile-${process.pid}`);

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

const COVERAGE_POLICY = [
  ["breakfast", "main", true],
  ["breakfast", "addition", false],
  ["breakfast", "drink", false],
  ["snack", "snack", true],
  ["lunch", "main", true],
  ["lunch", "addition", false],
  ["lunch", "drink", false],
  ["dinner", "main", true],
  ["dinner", "addition", false],
  ["dinner", "drink", false],
];

function startMockApi() {
  const requests = [];
  let dish = {
    id: "dish-soup",
    name: "Суп походный",
    recipe: { id: "recipe-soup", name: "Суп базовый", is_archived: false },
    meal_roles: [],
  };

  const readiness = () => {
    const coverage = COVERAGE_POLICY.map(([mealType, role, required]) => {
      const candidateCount = dish.meal_roles.some(
        (assignment) => assignment.role === role
          && assignment.allowed_meal_types.includes(mealType),
      ) ? 1 : 0;
      return {
        meal_type: mealType,
        role,
        required,
        candidate_count: candidateCount,
        minimum_required: 1,
        ready: candidateCount >= 1,
      };
    });
    return {
      ready: coverage.filter((item) => item.required).every((item) => item.ready),
      active_dish_count: 1,
      classified_dish_count: dish.meal_roles.length > 0 ? 1 : 0,
      unclassified_dish_count: dish.meal_roles.length > 0 ? 0 : 1,
      coverage,
    };
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

      if (request.method === "GET" && url.pathname === "/api/v1/dishes/catalogue-readiness") {
        sendJson(200, readiness());
        return;
      }
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
          items: [{
            id: "recipe-soup",
            name: "Суп базовый",
            component_count: 1,
            note_count: 0,
            is_archived: false,
          }],
        });
        return;
      }
      if (request.method === "PUT" && url.pathname === "/api/v1/dishes/dish-soup/meal-roles") {
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
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? "Browser evaluation failed");
    return result.result?.value;
  }

  close() {
    this.socket.close();
  }
}

async function waitForExpression(client, expression, description, timeoutMs = 10_000) {
  const deadline = Date.now() + timeoutMs;
  let lastError;
  while (Date.now() < deadline) {
    try {
      if (await client.evaluate(`Boolean(${expression})`)) return;
      lastError = undefined;
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  throw new Error(
    `Timed out waiting for ${description}${lastError ? `: ${lastError.message}` : ""}`,
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

async function setViewport(client, width, height) {
  await client.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: width <= 480,
  });
  await client.evaluate("new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))");
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
  const mockApi = startMockApi();
  await mockApi.listen();

  const vite = spawn(process.execPath, [
    path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
    "--host", "127.0.0.1", "--port", String(frontendPort), "--strictPort",
  ], {
    cwd: frontendRoot,
    env: { ...process.env, VITE_PROXY_TARGET: `http://127.0.0.1:${apiPort}` },
    stdio: "ignore",
  });
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
    await setViewport(client, 1280, 950);
    await client.send("Page.navigate", { url: fixtureUrl });

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Каталог не готов к автогенерации")
        && document.body?.innerText?.includes("Завтрак: нужно добавить основное блюдо.")
        && document.body?.innerText?.includes("Перекус: нужно добавить блюдо для перекуса.")
        && document.body?.innerText?.includes("Без ролей осталось блюд: 1 из 1.")`,
      "initial catalogue readiness warnings",
    );

    await clickButtonByText(client, "Настроить роли");
    await clickCheckboxByAriaLabel(client, "Назначить роль «Основное блюдо»");
    for (const mealLabel of ["Завтрак", "Обед", "Ужин"]) {
      await clickCheckboxByAriaLabel(
        client,
        `Разрешить роль «Основное блюдо» для приёма пищи «${mealLabel}»`,
      );
    }
    await clickCheckboxByAriaLabel(client, "Назначить роль «Перекус»");
    await clickCheckboxByAriaLabel(
      client,
      "Разрешить роль «Перекус» для приёма пищи «Перекус»",
    );
    await clickButtonByText(client, "Сохранить роли");

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Обязательное покрытие каталога готово")
        && document.body?.innerText?.includes("Все активные блюда классифицированы: 1.")
        && document.body?.innerText?.includes("Рекомендуемое покрытие меню")`,
      "updated catalogue readiness",
    );

    const mutationRequest = mockApi.requests.findLast(
      (request) => request.method === "PUT"
        && request.path === "/api/v1/dishes/dish-soup/meal-roles",
    );
    assert.ok(mutationRequest, "Role mutation request was not observed");
    assert.deepEqual(JSON.parse(mutationRequest.body), {
      roles: [
        {
          role: "main",
          is_repeatable: false,
          allowed_meal_types: ["breakfast", "lunch", "dinner"],
        },
        {
          role: "snack",
          is_repeatable: false,
          allowed_meal_types: ["snack"],
        },
      ],
    });

    await assertNoHorizontalOverflow(client, 1280);
    await captureScreenshot(client, "dish-catalogue-readiness-desktop");
    await setViewport(client, 360, 850);
    await assertNoHorizontalOverflow(client, 360);
    await captureScreenshot(client, "dish-catalogue-readiness-mobile");

    client.close();
    console.log("Dish catalogue readiness browser acceptance passed.");
  } finally {
    await cleanup();
  }
}

run().catch(async (error) => {
  console.error(error);
  await mkdir(artifactDir, { recursive: true });
  await writeFile(
    path.join(artifactDir, "dish-catalogue-readiness-browser-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
