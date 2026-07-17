import type {
  AppearanceColorTokens,
  AppearanceThemeDraft,
  AppearanceThemeExport,
} from "../api/appearanceSettingsApi";

const HEX_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;
const COLOR_KEYS: Array<keyof AppearanceColorTokens> = [
  "primary",
  "secondary",
  "accent",
  "background",
  "paper",
  "sidebar",
  "appbar",
  "text_primary",
  "text_secondary",
  "divider",
  "success",
  "warning",
  "error",
];

function cloneTheme(draft: AppearanceThemeDraft): AppearanceThemeDraft {
  return {
    ...draft,
    light: { ...draft.light },
    dark: { ...draft.dark },
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function oneOf<T extends string>(value: unknown, allowed: readonly T[]): value is T {
  return typeof value === "string" && allowed.includes(value as T);
}

function parseColors(value: unknown, label: string): AppearanceColorTokens {
  if (!isRecord(value)) throw new Error(`В файле отсутствует раздел «${label}».`);
  const colors = {} as AppearanceColorTokens;
  for (const key of COLOR_KEYS) {
    const color = value[key];
    if (typeof color !== "string" || !HEX_COLOR_PATTERN.test(color)) {
      throw new Error(`Поле ${label}.${key} должно иметь формат #RRGGBB.`);
    }
    colors[key] = color.toUpperCase();
  }
  return colors;
}

export function createAppearanceThemeExport(
  draft: AppearanceThemeDraft,
): AppearanceThemeExport {
  return {
    schema: "tourhub-appearance-theme",
    schema_version: 1,
    exported_at: new Date().toISOString(),
    theme: cloneTheme(draft),
  };
}

export function parseAppearanceThemeExport(value: unknown): AppearanceThemeDraft {
  if (!isRecord(value)) throw new Error("Файл не содержит объект темы.");
  if (value.schema !== "tourhub-appearance-theme" || value.schema_version !== 1) {
    throw new Error("Неподдерживаемый формат или версия файла темы.");
  }
  if (!isRecord(value.theme)) throw new Error("В файле отсутствует раздел theme.");

  const theme = value.theme;
  if (!oneOf(theme.font_family, ["system", "modern", "humanist", "serif"] as const)) {
    throw new Error("Файл содержит неподдерживаемый шрифт.");
  }
  if (!oneOf(theme.density, ["comfortable", "compact"] as const)) {
    throw new Error("Файл содержит неподдерживаемую плотность интерфейса.");
  }
  if (!oneOf(theme.button_style, ["contained", "soft", "outlined"] as const)) {
    throw new Error("Файл содержит неподдерживаемый стиль кнопок.");
  }
  if (!oneOf(theme.card_style, ["outlined", "elevated", "flat"] as const)) {
    throw new Error("Файл содержит неподдерживаемый стиль карточек.");
  }
  if (
    typeof theme.border_radius !== "number" ||
    !Number.isInteger(theme.border_radius) ||
    theme.border_radius < 0 ||
    theme.border_radius > 24
  ) {
    throw new Error("Скругление должно быть целым числом от 0 до 24.");
  }
  if (typeof theme.shadows_enabled !== "boolean") {
    throw new Error("Поле shadows_enabled должно быть логическим значением.");
  }

  return {
    preset_name: "custom",
    font_family: theme.font_family,
    density: theme.density,
    border_radius: theme.border_radius,
    button_style: theme.button_style,
    card_style: theme.card_style,
    shadows_enabled: theme.shadows_enabled,
    light: parseColors(theme.light, "light"),
    dark: parseColors(theme.dark, "dark"),
  };
}
