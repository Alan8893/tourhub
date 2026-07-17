import assert from "node:assert/strict";
import test from "node:test";

import type { AppearanceThemeDraft } from "../src/features/system-settings/api/appearanceSettingsApi.ts";
import {
  createAppearanceThemeExport,
  parseAppearanceThemeExport,
} from "../src/features/system-settings/appearance/themeTransfer.ts";

function defaultDraft(): AppearanceThemeDraft {
  return {
    preset_name: "tourhub",
    font_family: "system",
    density: "comfortable",
    border_radius: 10,
    button_style: "contained",
    card_style: "outlined",
    shadows_enabled: true,
    light: {
      primary: "#1B5E20",
      secondary: "#2E7D32",
      accent: "#F9A825",
      background: "#F4F7F4",
      paper: "#FFFFFF",
      sidebar: "#E8F2E8",
      appbar: "#1B5E20",
      text_primary: "#162018",
      text_secondary: "#435348",
      divider: "#C8D2CA",
      success: "#2E7D32",
      warning: "#ED6C02",
      error: "#D32F2F",
    },
    dark: {
      primary: "#81C784",
      secondary: "#A5D6A7",
      accent: "#FFD54F",
      background: "#101713",
      paper: "#18211B",
      sidebar: "#1E2A22",
      appbar: "#16351D",
      text_primary: "#F2F7F3",
      text_secondary: "#C1CDC4",
      divider: "#405047",
      success: "#81C784",
      warning: "#FFB74D",
      error: "#EF9A9A",
    },
  };
}

test("round-trips a versioned appearance theme without runtime metadata", () => {
  const draft = defaultDraft();
  draft.preset_name = "ocean";
  draft.light.primary = "#075985";

  const exported = createAppearanceThemeExport(draft);
  const imported = parseAppearanceThemeExport(exported);

  assert.equal(exported.schema, "tourhub-appearance-theme");
  assert.equal(exported.schema_version, 1);
  assert.equal(imported.preset_name, "custom");
  assert.equal(imported.light.primary, "#075985");
  assert.equal("version" in exported.theme, false);
  assert.equal("updated_at" in exported.theme, false);
});

test("rejects malformed or unsupported theme imports", () => {
  assert.throws(
    () => parseAppearanceThemeExport({ schema: "other", schema_version: 1, theme: {} }),
    /Неподдерживаемый формат/,
  );

  const invalid = createAppearanceThemeExport(defaultDraft());
  invalid.theme.light.primary = "green";
  assert.throws(() => parseAppearanceThemeExport(invalid), /light.primary/);

  const invalidRadius = createAppearanceThemeExport(defaultDraft());
  invalidRadius.theme.border_radius = 25;
  assert.throws(() => parseAppearanceThemeExport(invalidRadius), /от 0 до 24/);
});
