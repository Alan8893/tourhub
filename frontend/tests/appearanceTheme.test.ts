import assert from "node:assert/strict";
import test from "node:test";

import {
  DEFAULT_APPEARANCE,
  cloneAppearanceDraft,
  createTourHubTheme,
} from "../src/features/system-settings/appearance/theme.ts";
import {
  createAppearanceThemeExport,
  parseAppearanceThemeExport,
} from "../src/features/system-settings/appearance/themeTransfer.ts";

function defaultDraft() {
  const {
    version: _version,
    updated_at: _updatedAt,
    ...draft
  } = DEFAULT_APPEARANCE;
  return cloneAppearanceDraft(draft);
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

test("creates distinct light and dark Material UI themes", () => {
  const draft = defaultDraft();
  const light = createTourHubTheme(draft, "light");
  const dark = createTourHubTheme(draft, "dark");

  assert.equal(light.palette.mode, "light");
  assert.equal(light.palette.background.default, "#F4F7F4");
  assert.equal(dark.palette.mode, "dark");
  assert.equal(dark.palette.background.default, "#101713");
  assert.equal(light.shape.borderRadius, 10);
});
