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
  DEFAULT_MODULE_SETTINGS,
  ModuleSettings,
  getModuleSettings,
} from "../api/moduleSettingsApi";

interface ModuleVisibilityContextValue {
  settings: ModuleSettings;
  isLoaded: boolean;
  applySavedSettings: (settings: ModuleSettings) => void;
  reloadModuleSettings: () => Promise<void>;
}

const ModuleVisibilityContext = createContext<ModuleVisibilityContextValue | null>(null);

export default function ModuleVisibilityProvider({ children }: PropsWithChildren) {
  const [settings, setSettings] = useState<ModuleSettings>(DEFAULT_MODULE_SETTINGS);
  const [isLoaded, setIsLoaded] = useState(false);

  const reloadModuleSettings = useCallback(async () => {
    try {
      setSettings(await getModuleSettings());
    } catch {
      setSettings(DEFAULT_MODULE_SETTINGS);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  useEffect(() => {
    void reloadModuleSettings();
  }, [reloadModuleSettings]);

  const applySavedSettings = useCallback((updated: ModuleSettings) => {
    setSettings(updated);
    setIsLoaded(true);
  }, []);

  const value = useMemo<ModuleVisibilityContextValue>(
    () => ({ settings, isLoaded, applySavedSettings, reloadModuleSettings }),
    [applySavedSettings, isLoaded, reloadModuleSettings, settings],
  );

  return (
    <ModuleVisibilityContext.Provider value={value}>
      {children}
    </ModuleVisibilityContext.Provider>
  );
}

export function useModuleVisibility(): ModuleVisibilityContextValue {
  const context = useContext(ModuleVisibilityContext);
  if (!context) {
    throw new Error("useModuleVisibility must be used inside ModuleVisibilityProvider");
  }
  return context;
}
