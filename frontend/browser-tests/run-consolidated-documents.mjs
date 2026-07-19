import assert from "node:assert/strict";
import { spawn } from "node:child_process";
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
import {
  requests,
  startConsolidatedDocumentsApi,
} from "./consolidated-documents-fixture.mjs";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const artifactDir = path.join(frontendRoot, "browser-test-artifacts");
const pageUrl = "http://127.0.0.1:5194/browser-tests/consolidated-documents.html";
const profileDir = "/tmp/tourhub-consolidated-documents-profile";

async function clickButton(client, label) {
  const clicked = await client.evaluate(`(() => {
    const button = [...document.querySelectorAll("button")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(label)},
    );
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
  assert.equal(clicked, true, `Could not click ${label}`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startConsolidatedDocumentsApi();
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
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18094" },
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
      "--remote-debugging-port=9248",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9248/json/version");
    const targets = await fetch("http://127.0.0.1:9248/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) =>
      item.url.includes("consolidated-documents.html"),
    );
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
      `document.body?.innerText?.includes("Полный комплект") &&
       document.body.innerText.includes("Полный PDF") &&
       document.body.innerText.includes("Полный Excel") &&
       document.body.innerText.includes("Скачать полный пакет") &&
       document.body.innerText.includes("Отдельные документы")`,
      "consolidated document controls",
    );

    const actions = [
      ["Полный PDF", "/api/v1/projects/91/documents/consolidated/pdf"],
      ["Полный Excel", "/api/v1/projects/91/documents/consolidated/excel"],
      ["Скачать полный пакет", "/api/v1/projects/91/documents/package"],
    ];
    for (const [label, requestPath] of actions) {
      await clickButton(client, label);
      for (let attempt = 0; attempt < 100; attempt += 1) {
        if (
          requests.some(
            (request) =>
              request.method === "GET" && request.path === requestPath,
          )
        ) {
          break;
        }
        await sleep(50);
      }
      assert.ok(
        requests.some(
          (request) =>
            request.method === "GET" && request.path === requestPath,
        ),
        `Request not observed: ${requestPath}`,
      );
    }

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(300);
    const layout = await client.evaluate(`({
      clientWidth: document.documentElement.clientWidth,
      scrollWidth: document.documentElement.scrollWidth,
      bodyScrollWidth: document.body.scrollWidth,
    })`);
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
      path.join(artifactDir, "consolidated-documents-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Consolidated documents browser acceptance passed.");
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
    path.join(artifactDir, "consolidated-documents-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
