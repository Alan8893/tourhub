import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import {
  requests,
  startDocumentAppearanceApi,
} from "./document-appearance-settings-fixture.mjs";
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
const pageUrl = "http://127.0.0.1:5183/browser-tests/document-appearance-settings.html";
const profileDir = "/tmp/tourhub-document-appearance-settings-profile";

async function setFieldByLabel(client, labelText, value) {
  return client.evaluate(`(() => {
    const label = [...document.querySelectorAll("label")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(labelText)},
    );
    const control = label?.htmlFor ? document.getElementById(label.htmlFor) : null;
    if (!control) return false;
    const prototype = control instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(prototype, "value")?.set;
    setter?.call(control, ${JSON.stringify(value)});
    control.dispatchEvent(new Event("input", { bubbles: true }));
    return true;
  })()`);
}

async function selectMuiOption(client, labelText, optionText) {
  const opened = await client.evaluate(`(() => {
    const normalize = (value) => (value ?? "").replace(/\\s+/g, " ").trim();
    const controls = [...document.querySelectorAll('[role="combobox"]')];
    const control = controls.find((candidate) => {
      const labelledBy = (candidate.getAttribute("aria-labelledby") ?? "").split(/\\s+/);
      return labelledBy.some(
        (id) => normalize(document.getElementById(id)?.textContent) === ${JSON.stringify(labelText)},
      );
    });
    if (!control) return false;
    control.dispatchEvent(new MouseEvent("mousedown", {
      bubbles: true,
      cancelable: true,
      button: 0,
    }));
    return true;
  })()`);
  assert.equal(opened, true, `Select not found: ${labelText}`);
  await waitForExpression(
    client,
    `[...document.querySelectorAll('[role="option"]')].some(
      (item) => item.textContent?.trim() === ${JSON.stringify(optionText)},
    )`,
    `option ${optionText}`,
  );
  const selected = await client.evaluate(`(() => {
    const option = [...document.querySelectorAll('[role="option"]')].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(optionText)},
    );
    if (!option) return false;
    option.click();
    return true;
  })()`);
  assert.equal(selected, true, `Option not found: ${optionText}`);
}

async function clickLabel(client, labelText) {
  return client.evaluate(`(() => {
    const label = [...document.querySelectorAll("label")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(labelText)},
    );
    if (!label) return false;
    label.click();
    return true;
  })()`);
}

async function clickButton(client, text) {
  return client.evaluate(`(() => {
    const button = [...document.querySelectorAll("button")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(text)},
    );
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
}

async function run() {
  await rm(profileDir, { recursive: true, force: true });
  await mkdir(artifactDir, { recursive: true });
  const api = startDocumentAppearanceApi();
  await api.listen();
  const vite = spawn(
    process.execPath,
    [
      path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js"),
      "--host",
      "127.0.0.1",
      "--port",
      "5183",
      "--strictPort",
    ],
    {
      cwd: frontendRoot,
      env: { ...process.env, VITE_PROXY_TARGET: "http://127.0.0.1:18085" },
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
      "--remote-debugging-port=9235",
      `--user-data-dir=${profileDir}`,
      pageUrl,
    ],
    { stdio: "ignore" },
  );

  try {
    await waitForHttp("http://127.0.0.1:9235/json/version");
    const targets = await fetch("http://127.0.0.1:9235/json/list").then((response) =>
      response.json(),
    );
    const target = targets.find((item) => item.url.includes("document-appearance-settings.html"));
    assert.ok(target?.webSocketDebuggerUrl);
    const client = await CdpClient.connect(target.webSocketDebuggerUrl);
    await client.send("Runtime.enable");
    await client.send("Page.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 1280,
      height: 1000,
      deviceScaleFactor: 1,
      mobile: false,
    });
    await sleep(250);

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Документы") &&
       document.body?.innerText?.includes("Предпросмотр документа") &&
       document.body?.innerText?.includes("Турклуб Север") &&
       [...document.querySelectorAll("button")].some(
         (item) => item.textContent?.trim() === "Сохранить раздел",
       )`,
      "loaded document appearance editor",
    );

    assert.equal(await setFieldByLabel(client, "Основной цвет", "#075985"), true);
    assert.equal(
      await setFieldByLabel(
        client,
        "Пользовательский footer",
        "Турклуб Север · внутренний документ",
      ),
      true,
    );
    await selectMuiOption(client, "Плотность таблиц", "Компактная");
    await selectMuiOption(client, "Логотип документов", "Изображение для документов");
    assert.equal(
      await clickLabel(
        client,
        "Использовать изображение документов как фон титульного блока",
      ),
      true,
    );

    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Турклуб Север · внутренний документ") &&
       document.querySelector('[aria-label="Предпросмотр документа"]')`,
      "updated isolated document preview",
    );

    assert.equal(await clickButton(client, "Сохранить раздел"), true);
    await waitForExpression(
      client,
      `document.body?.innerText?.includes("Оформление документов сохранено") &&
       document.body?.innerText?.includes("основной цвет документов") &&
       document.body?.innerText?.includes("footer документов")`,
      "saved document appearance and history",
    );
    await waitForExpression(
      client,
      `[...document.querySelectorAll("button")].some(
        (item) => item.textContent?.trim() === "Сохранить раздел" && item.disabled,
      )`,
      "settled document appearance save state",
    );

    const update = requests.find(
      (item) => item.method === "PUT" && item.path === "/api/v1/settings/documents",
    );
    assert.equal(update?.body.expected_version, 1);
    assert.equal(update?.body.primary_color, "#075985");
    assert.equal(update?.body.table_density, "compact");
    assert.equal(update?.body.logo_source, "document_image");
    assert.equal(update?.body.use_document_image_as_title_background, true);
    assert.equal(update?.body.footer_text, "Турклуб Север · внутренний документ");

    await client.send("Emulation.setDeviceMetricsOverride", {
      width: 360,
      height: 900,
      deviceScaleFactor: 1,
      mobile: true,
    });
    await sleep(450);
    const layout = await client.evaluate(`(() => {
      const clientWidth = document.documentElement.clientWidth;
      const describe = (element) => {
        const rect = element.getBoundingClientRect();
        return {
          tag: element.tagName,
          className: String(element.className || "").slice(0, 180),
          text: (element.textContent || "").replace(/\\s+/g, " ").trim().slice(0, 120),
          left: Math.round(rect.left * 100) / 100,
          right: Math.round(rect.right * 100) / 100,
          width: Math.round(rect.width * 100) / 100,
          clientWidth: element.clientWidth,
          scrollWidth: element.scrollWidth,
          overflowX: getComputedStyle(element).overflowX,
        };
      };
      const wideElements = [...document.querySelectorAll("body *")]
        .map(describe)
        .filter((item) => item.right > clientWidth + 1 || item.left < -1)
        .sort((first, second) => second.right - first.right)
        .slice(0, 12);
      return {
        clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
        bodyScrollWidth: document.body.scrollWidth,
        hasPreview: document.body?.innerText?.includes("Предпросмотр документа"),
        hasSave: [...document.querySelectorAll("button")].some(
          (item) => item.textContent?.trim() === "Сохранить раздел",
        ),
        wideElements,
      };
    })()`);
    await writeFile(
      path.join(artifactDir, "document-appearance-settings-layout.json"),
      JSON.stringify(layout, null, 2),
    );
    const noOverflow =
      layout.scrollWidth <= layout.clientWidth + 1 &&
      layout.bodyScrollWidth <= layout.clientWidth + 1;
    assert.ok(noOverflow, `Mobile overflow diagnostics: ${JSON.stringify(layout)}`);
    assert.equal(layout.hasPreview, true);
    assert.equal(layout.hasSave, true);

    const screenshot = await client.send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });
    await writeFile(
      path.join(artifactDir, "document-appearance-settings-mobile.png"),
      Buffer.from(screenshot.data, "base64"),
    );
    client.close();
    console.log("Document appearance settings browser acceptance passed.");
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
    path.join(artifactDir, "document-appearance-settings-error.txt"),
    `${error?.stack ?? error}\n`,
  );
  process.exitCode = 1;
});
