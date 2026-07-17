import assert from "node:assert/strict";
import { rm } from "node:fs/promises";

import { sleep, waitForExpression } from "./club-settings-cdp.mjs";

export async function removeChromeProfile(
  profileDir,
  { allowResidual = false } = {},
) {
  let lastError;
  for (let attempt = 0; attempt < 30; attempt += 1) {
    try {
      await rm(profileDir, { recursive: true, force: true });
      return;
    } catch (error) {
      if (error?.code !== "ENOTEMPTY") throw error;
      lastError = error;
      await sleep(50);
    }
  }
  if (allowResidual) return;
  throw lastError;
}

export async function waitForPageTarget(
  debuggingPort,
  urlFragment,
  timeoutMs = 15_000,
) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const targets = await fetch(`http://127.0.0.1:${debuggingPort}/json/list`).then(
      (response) => response.json(),
    );
    const target = targets.find(
      (candidate) =>
        candidate.type === "page" && candidate.url.includes(urlFragment),
    );
    if (target?.webSocketDebuggerUrl) return target;
    await sleep(100);
  }
  throw new Error(`Chrome page target was not found: ${urlFragment}`);
}

export async function setInput(client, selector, value) {
  const changed = await client.evaluate(`(() => {
    const input = document.querySelector(${JSON.stringify(selector)});
    if (!input) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, ${JSON.stringify(value)});
    input.dispatchEvent(new Event("input", { bubbles: true }));
    return true;
  })()`);
  assert.equal(changed, true, `Input not found: ${selector}`);
}

export async function setNumberInput(client, index, value) {
  const changed = await client.evaluate(`(() => {
    const input = document.querySelectorAll('input[type="number"]')[${index}];
    if (!input) return false;
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
    setter.call(input, ${JSON.stringify(value)});
    input.dispatchEvent(new Event("input", { bubbles: true }));
    return true;
  })()`);
  assert.equal(changed, true, `Number input ${index} not found`);
}

export async function clickButton(client, label) {
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

export async function waitForRequest(requests, method, requestPath, count = 1) {
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    const matches = requests.filter(
      (request) => request.method === method && request.path === requestPath,
    );
    if (matches.length >= count) return matches;
    await sleep(50);
  }
  assert.fail(`${method} ${requestPath} was not observed ${count} time(s)`);
}
