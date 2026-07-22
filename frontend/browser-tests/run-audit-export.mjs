import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  auditExportRequests,
  startAuditExportApi,
} from "./audit-export-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5207/browser-tests/audit-log.html";
const chromeDebugUrl = "http://127.0.0.1:9259";
const profileDir = `/tmp/tourhub-audit-export-profile-${process.pid}`;
const removeProfile = () =>
  rm(profileDir, {
    recursive: true,
    force: true,
    maxRetries: 10,
    retryDelay: 100,
  });

async function waitForRequest(pathname, description) {
  for (let attempt = 0; attempt < 100; attempt += 1) {
    const request = auditExportRequests.find((item) => item.path === pathname);
    if (request) return request;
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function writeDiagnostics(client, error) {
  const page = client
    ? await client.evaluate(`(() => ({
        href: location.href,
        bodyText: document.body?.innerText ?? "",
        bodyHtml: document.body?.innerHTML?.slice(0, 30000) ?? "",
      }))()`)
    : null;
  await writeFile(
    path.join(artifactDir, "audit-export-error.txt"),
    JSON.stringify(
      {
        error: error?.stack ?? String(error),
        page,
        requests: auditExportRequests,
      },
      null,
      2,
    ),
  );
}

async function run() {
  await removeProfile();
  await mkdir(artifactDir, { recursive: true });
  const api = startAuditExportApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5207",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18110" },
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
      "--remote-debugging-port=9259",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );
  let client;

  try {
    await waitForHttp(`${chromeDebugUrl}/json/version`);
    const targets = await fetch(`${chromeDebugUrl}/json/list`).then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("audit-log.html"));
    assert.ok(target?.webSocketDebuggerUrl);
    client = await CdpClient.connect(target.webSocketDebuggerUrl);
    await client.send("Runtime.enable");
    await client.send("Page.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
    });

    await waitForRequest("/api/v1/audit/events", "initial audit list request");
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Аудит действий") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Скачать CSV",
       ) &&
       document.body?.innerText?.includes("Анна Администратор")`,
      "loaded audit CSV export surface",
    );

    const filterChanged = await client.evaluate(`(() => {
      const input = document.querySelector('input[placeholder="Например: document_generated"]');
      if (!input) return false;
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
      setter?.call(input, "document_generated");
      input.dispatchEvent(new Event("input", { bubbles: true }));
      return true;
    })()`);
    assert.equal(filterChanged, true);
    await sleep(150);

    const clicked = await client.evaluate(`(() => {
      const button = [...document.querySelectorAll("button")].find(
        (item) => item.textContent?.trim() === "Скачать CSV",
      );
      button?.click();
      return Boolean(button);
    })()`);
    assert.equal(clicked, true);

    const request = await waitForRequest(
      "/api/v1/audit/events/export.csv",
      "audit CSV export request",
    );
    assert.equal(request.method, "GET");
    assert.equal(request.query.action, "document_generated");

    const csvText = await client.evaluate(`fetch(
      "/api/v1/audit/events/export.csv?action=document_generated",
    ).then((response) => response.text())`);
    assert.ok(csvText.includes("actor_display_name"));
    assert.ok(csvText.includes("Анна Администратор"));
    assert.ok(csvText.includes("document_generated"));
    assert.ok(csvText.includes("Поход на Ладогу"));

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(350);
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

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "audit-export-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    client = undefined;
    console.log("Audit CSV export browser acceptance passed.");
  } catch (error) {
    await writeDiagnostics(client, error);
    throw error;
  } finally {
    client?.close();
    await Promise.allSettled([stopProcess(chrome), stopProcess(vite)]);
    await api.close();
    await removeProfile();
  }
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
