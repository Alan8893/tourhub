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

async function readBody(request) {
  const chunks = [];
  for await (const chunk of request) chunks.push(chunk);
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function startApi() {
  let settings = { club_name: "Турклуб Север", logo_data_url: null };
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
    const body = request.method === "PUT" ? await readBody(request) : undefined;
    requests.push({ method: request.method, path: url.pathname, body });
    response.setHeader("content-type", "application/json");
    if (url.pathname !== "/api/v1/club-settings") {
      response.statusCode = 404;
      response.end(JSON.stringify({ detail: "not found" }));
      return;
    }
    if (request.method === "PUT") {
      settings = { club_name: body.club_name, logo_data_url: null };
    }
    response.statusCode = 200;
    response.end(JSON.stringify(settings));
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

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки клуба") &&
       document.querySelector('input[type="text"]')?.value === "Турклуб Север"`,
      "loaded club settings",
    );
    assert.equal(
      await client.evaluate(`(() => {
        const input = document.querySelector('input[type="text"]');
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
          (item) => item.textContent.trim() === "Сохранить настройки",
        );
        if (!button || button.disabled) return false;
        button.click();
        return true;
      })()`),
      true,
    );
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Настройки клуба сохранены")`,
      "save confirmation",
    );
    const put = requests.find((item) => item.method === "PUT");
    assert.deepEqual(put?.body, {
      club_name: "Турклуб Полюс",
      logo_data_url: null,
      remove_logo: false,
    });

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
    );
    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "club-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Club settings browser acceptance passed.");
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
