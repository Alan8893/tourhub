import assert from "node:assert/strict";

import { sleep, waitForExpression } from "./club-settings-cdp.mjs";

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
