import { ThemeProvider } from "@mui/material/styles";
import {
  PropsWithChildren,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AppearanceSettings,
  DisplayModePreference,
  ResolvedDisplayMode,
  getAppearanceSettings,
} from "../api/appearanceSettingsApi";
import { DEFAULT_APPEARANCE, createTourHubTheme } from "../appearance/theme";

const DISPLAY_MODE_KEY = "tourhub.display-mode";

interface AppearanceContextValue {
  settings: AppearanceSettings;
  displayMode: DisplayModePreference;
  resolvedMode: ResolvedDisplayMode;
  isLoaded: boolean;
  setDisplayMode: (mode: DisplayModePreference) => void;
  applySavedSettings: (settings: AppearanceSettings) => void;
  reloadAppearance: () => Promise<void>;
}

const AppearanceContext = createContext<AppearanceContextValue | null>(null);

function readDisplayMode(): DisplayModePreference {
  const stored = window.localStorage.getItem(DISPLAY_MODE_KEY);
  if (stored === "light" || stored === "dark" || stored === "system") return stored;
  return "system";
}

export default function AppearanceProvider({ children }: PropsWithChildren) {
  const [settings, setSettings] = useState<AppearanceSettings>(DEFAULT_APPEARANCE);
  const [displayMode, setDisplayModeState] = useState<DisplayModePreference>(readDisplayMode);
  const [systemDark, setSystemDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
  );
  const [isLoaded, setIsLoaded] = useState(false);

  const reloadAppearance = useCallback(async () => {
    try {
      setSettings(await getAppearanceSettings());
    } catch {
      setSettings(DEFAULT_APPEARANCE);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  useEffect(() => {
    void reloadAppearance();
  }, [reloadAppearance]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (event: MediaQueryListEvent) => setSystemDark(event.matches);
    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, []);

  const setDisplayMode = useCallback((mode: DisplayModePreference) => {
    window.localStorage.setItem(DISPLAY_MODE_KEY, mode);
    setDisplayModeState(mode);
  }, []);

  const applySavedSettings = useCallback((updated: AppearanceSettings) => {
    setSettings(updated);
    setIsLoaded(true);
  }, []);

  const resolvedMode: ResolvedDisplayMode =
    displayMode === "system" ? (systemDark ? "dark" : "light") : displayMode;
  const theme = useMemo(
    () => createTourHubTheme(settings, resolvedMode),
    [resolvedMode, settings],
  );

  const value = useMemo<AppearanceContextValue>(
    () => ({
      settings,
      displayMode,
      resolvedMode,
      isLoaded,
      setDisplayMode,
      applySavedSettings,
      reloadAppearance,
    }),
    [
      applySavedSettings,
      displayMode,
      isLoaded,
      reloadAppearance,
      resolvedMode,
      setDisplayMode,
      settings,
    ],
  );

  return (
    <AppearanceContext.Provider value={value}>
      <ThemeProvider theme={theme}>{children}</ThemeProvider>
    </AppearanceContext.Provider>
  );
}

export function useAppearance(): AppearanceContextValue {
  const context = useContext(AppearanceContext);
  if (!context) throw new Error("useAppearance must be used inside AppearanceProvider");
  return context;
}
