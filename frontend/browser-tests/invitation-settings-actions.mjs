import assert from "node:assert/strict";

import { waitForExpression } from "./club-settings-cdp.mjs";

export async function setFieldByLabel(client, labelText, value) {
  return client.evaluate(`(() => {
    const normalize = (text) => (text ?? "")
      .replace(/\\s+/g, " ")
      .replace(/\\s*\\*$/, "")
      .trim();
    const label = [...document.querySelectorAll("label")].find(
      (item) => normalize(item.textContent) === ${JSON.stringify(labelText)},
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

export async function selectMuiOption(client, labelText, optionText) {
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

export async function clickLabel(client, labelText) {
  return client.evaluate(`(() => {
    const label = [...document.querySelectorAll("label")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(labelText)},
    );
    if (!label) return false;
    label.click();
    return true;
  })()`);
}

export async function clickButton(client, text) {
  return client.evaluate(`(() => {
    const button = [...document.querySelectorAll("button")].find(
      (item) => item.textContent?.trim() === ${JSON.stringify(text)},
    );
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
}
