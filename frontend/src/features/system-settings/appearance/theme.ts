import { createTheme, getContrastRatio } from "@mui/material/styles";
import type { Theme } from "@mui/material/styles";

import type {
  AppearanceSettings,
  AppearanceThemeDraft,
  ResolvedDisplayMode,
} from "../api/appearanceSettingsApi";

const FONT_STACKS: Record<AppearanceThemeDraft["font_family"], string> = {
  system: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  modern: '"Trebuchet MS", "Segoe UI", sans-serif',
  humanist: 'Verdana, Geneva, "Segoe UI", sans-serif',
  serif: 'Georgia, "Times New Roman", serif',
};

export const DEFAULT_APPEARANCE: AppearanceSettings = {
  version: 1,
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
  updated_at: "",
};

function contrastText(background: string): string {
  return getContrastRatio(background, "#FFFFFF") >= 4.5 ? "#FFFFFF" : "#111111";
}

function alphaHex(color: string, alpha: string): string {
  return `${color}${alpha}`;
}

export function createTourHubTheme(
  settings: AppearanceThemeDraft,
  mode: ResolvedDisplayMode,
): Theme {
  const tokens = mode === "light" ? settings.light : settings.dark;
  const compact = settings.density === "compact";
  const buttonVariant = settings.button_style === "outlined" ? "outlined" : "contained";
  const cardVariant = settings.card_style === "outlined" ? "outlined" : undefined;
  const appbarText = contrastText(tokens.appbar);

  return createTheme({
    spacing: compact ? 6 : 8,
    shape: { borderRadius: settings.border_radius },
    typography: {
      fontFamily: FONT_STACKS[settings.font_family],
      button: { textTransform: "none", fontWeight: 600 },
    },
    palette: {
      mode,
      contrastThreshold: 4.5,
      primary: { main: tokens.primary },
      secondary: { main: tokens.secondary },
      info: { main: tokens.accent },
      success: { main: tokens.success },
      warning: { main: tokens.warning },
      error: { main: tokens.error },
      background: {
        default: tokens.background,
        paper: tokens.paper,
      },
      text: {
        primary: tokens.text_primary,
        secondary: tokens.text_secondary,
      },
      divider: tokens.divider,
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            backgroundColor: tokens.background,
            color: tokens.text_primary,
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: tokens.appbar,
            color: appbarText,
            boxShadow: settings.shadows_enabled ? undefined : "none",
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: tokens.sidebar,
            color: tokens.text_primary,
            borderColor: tokens.divider,
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: settings.border_radius,
            marginInline: 6,
            "&.Mui-selected": {
              backgroundColor: alphaHex(tokens.accent, mode === "light" ? "22" : "33"),
            },
          },
        },
      },
      MuiButton: {
        defaultProps: {
          variant: buttonVariant,
          size: compact ? "small" : "medium",
        },
        styleOverrides: {
          root: {
            borderRadius: settings.border_radius,
            boxShadow: settings.shadows_enabled ? undefined : "none",
            ...(settings.button_style === "soft"
              ? {
                  backgroundColor: alphaHex(tokens.primary, mode === "light" ? "1F" : "33"),
                  color: tokens.primary,
                  boxShadow: "none",
                  "&:hover": {
                    backgroundColor: alphaHex(
                      tokens.primary,
                      mode === "light" ? "2E" : "44",
                    ),
                    boxShadow: "none",
                  },
                }
              : {}),
          },
        },
      },
      MuiCard: {
        defaultProps: {
          variant: cardVariant,
          elevation:
            settings.card_style === "elevated" && settings.shadows_enabled ? 3 : 0,
        },
        styleOverrides: {
          root: {
            backgroundColor: tokens.paper,
            borderColor: tokens.divider,
            boxShadow:
              settings.card_style === "elevated" && settings.shadows_enabled
                ? undefined
                : "none",
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
          },
        },
      },
      MuiTextField: {
        defaultProps: {
          size: compact ? "small" : "medium",
        },
      },
      MuiFormControl: {
        defaultProps: {
          size: compact ? "small" : "medium",
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            padding: compact ? "8px 10px" : undefined,
            borderColor: tokens.divider,
          },
          head: {
            fontWeight: 700,
            backgroundColor: alphaHex(tokens.primary, mode === "light" ? "0F" : "1F"),
          },
        },
      },
    },
  });
}

export function cloneAppearanceDraft(settings: AppearanceThemeDraft): AppearanceThemeDraft {
  return {
    ...settings,
    light: { ...settings.light },
    dark: { ...settings.dark },
  };
}
