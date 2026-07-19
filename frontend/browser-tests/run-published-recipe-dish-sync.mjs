import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdir, rm, writeFile } from "node:fs/promises";
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
const pageUrl = "http://127.0.0.1:5194/browser-tests/published-recipe-dish-sync.html";
const profileDir = "/tmp/tourhub-published-recipe-dish-profile";
const requests = [];

const recipe = {
  id: "recipe-published",
  name: "Суп после публикации",
  component_count: 2,
  note_count: 0,
  is_archived: false,
  scope: "club",
  owner_user_id: null,
  owner_display_name: null,
  is_owned_by_current_user: false,
  lifecycle_status: "published",
  submitted_by_user_id: 7,
  submitted_by_display_name: "Автор рецепта",
  submitted_at: "2026-07-19T12:00:00+00:00",
  reviewed_by_user_id: 2,
  reviewed_by_display_name: "Проверяющий",
  reviewed_at: "2026-07-19T12:30:00+00:00",
  review_comment: null,
  can_edit: false,
  can_archive: false,
  can_restore: false,
  can_delete: false,
  can_submit: false,
  can_publish: false,
  can_reject: false,
};

let dish = {
  id: "dish-published",
  name: recipe.name,
  recipe: {
    id: recipe.id,
    name: recipe.name,
    is_archived: false,
    scope: "club",
    owner_display_name: null,
    is_default: true,
  },
  recipes: [
    {
      id: recipe.id,
      name: recipe.name,
      is_archived: false,
      scope: "club",
      owner_display_name: null,
      is_default: true,
    },
  ],
  meal_roles: [],
};

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  const content = Buffer.concat(chunks).toString("utf8");
  return content ? JSON.parse(content) : undefined;
}

function startMockApi() {
  requests.length = 0;
  dish = { ...dish, meal_roles: [] };
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = ["POST", "PUT", "PATCH"].includes(request.method ?? "")
      ? await readBody(request)
      : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");

    if (request.method === "GET" && url.pathname === "/api/v1/dishes") {
      response.end(JSON.stringify({ items: [dish] }));
      return;
    }
    if (request.method === "GET" && url.pathname === `/api/v1/dishes/${dish.id}`) {
      response.end(JSON.stringify(dish));
      return;
    }
    if (request.method === "GET" && url.pathname === "/api/v1/recipes") {
      response.end(JSON.stringify({ items: [recipe] }));
      return;
    }
    if (
      request.method === "PUT" &&
      url.pathname === `/api/v1/dishes/${dish.id}/meal-roles`
    ) {
      dish = { ...dish, meal_roles: body.roles };
      response.end(JSON.stringify(dish));
      return;
    }

    response.statusCode = 404;
    response.end(JSON.stringify({ error: `Unhandled mock path: ${url.pathname}` }));
  });

  return {
    listen: () => new Promise((resolve) => server.listen(18104, "127.0.0.1", resolve)),
    close: () =>
      new Promise((resolve) => {
        server.closeAllConnections();
        server.close(resolve);
      }),
  };
}

async function clickButton(client, text) {
  const clicked = await client.evaluate(`(() => {
    const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
    const button = [...document.querySelectorAll("button")].find(
      (item) => normalize(item.textContent) === ${JSON.stringify(text)} && !item.disabled,
    );
    if (!button) return false;
    button.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Button not found: ${text}`);
}

async function clickCheckbox(client, ariaLabel) {
  const clicked = await client.evaluate(`(() => {
    const input = document.querySelector(${JSON.stringify(`input[aria-label="${ariaLabel}"]`)});
    if (!input || input.disabled) return false;
    input.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Checkbox not found: ${ariaLabel}`);
}

async function assertNoHorizontalOverflow(client) {
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
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startMockApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5194",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18104" },
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
      "--remote-debugging-port=9250",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9250/json/version");
    const targets = await fetch("http://127.0.0.1:9250/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("published-recipe-dish-sync.html"));
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
      `document.body?.innerText?.includes("Суп после публикации") &&
       document.body?.innerText?.includes("Не настроено для генератора") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Настроить генератор",
       )`,
      "published Dish generator warning",
    );
    await clickButton(client, "Настроить генератор");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Роли блюда «Суп после публикации»")`,
      "generator role dialog",
    );
    await clickCheckbox(client, "Назначить роль «Основное блюдо»");
    await clickCheckbox(
      client,
      "Разрешить роль «Основное блюдо» для приёма пищи «Ужин»",
    );
    await clickButton(client, "Сохранить роли");

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Роли блюда сохранены.") &&
       document.body?.innerText?.includes("Готово для генератора") &&
       !document.body?.innerText?.includes("Не настроено для генератора")`,
      "generator-ready Dish state",
    );
    const roleRequest = requests.find(
      (item) =>
        item.method === "PUT" &&
        item.path === "/api/v1/dishes/dish-published/meal-roles",
    );
    assert.deepEqual(roleRequest?.body, {
      roles: [
        {
          role: "main",
          is_repeatable: false,
          allowed_meal_types: ["dinner"],
        },
      ],
    });

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 800,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(350);
    await assertNoHorizontalOverflow(client);
    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "published-recipe-dish-sync-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Published Recipe Dish synchronization browser acceptance passed.");
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
    path.join(artifactDir, "published-recipe-dish-sync-error.txt"),
    `${error?.stack ?? error}\n\nRequests:\n${JSON.stringify(requests, null, 2)}\n`,
  );
  process.exitCode = 1;
});
