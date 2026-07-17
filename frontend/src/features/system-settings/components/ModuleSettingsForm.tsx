import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Paper,
  Stack,
  Switch,
  Typography,
} from "@mui/material";
import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  DEFAULT_MODULE_SETTINGS,
  ModuleDefinition,
  ModuleKey,
  ModuleSettings,
  ModuleSettingsHistoryItem,
  ModuleVisibilityDraft,
  getModuleSettings,
  getModuleSettingsHistory,
  updateModuleSettings,
} from "../api/moduleSettingsApi";
import { useModuleVisibility } from "../providers/ModuleVisibilityProvider";
import SettingsHistoryList from "./SettingsHistoryList";

const FIELD_BY_KEY: Record<ModuleKey, keyof ModuleVisibilityDraft> = {
  projects: "projects_visible",
  catalogue: "catalogue_visible",
  catalog_import: "catalog_import_visible",
  shopping: "shopping_visible",
  equipment: "equipment_visible",
  documents: "documents_visible",
};

const LABEL_BY_KEY: Record<ModuleKey, string> = {
  projects: "Проекты",
  catalogue: "Каталог",
  catalog_import: "Импорт",
  shopping: "Закупка",
  equipment: "Оборудование",
  documents: "Документы",
};

function toDraft(settings: ModuleSettings): ModuleVisibilityDraft {
  return {
    projects_visible: settings.projects_visible,
    catalogue_visible: settings.catalogue_visible,
    catalog_import_visible: settings.catalog_import_visible,
    shopping_visible: settings.shopping_visible,
    equipment_visible: settings.equipment_visible,
    documents_visible: settings.documents_visible,
  };
}

function draftLockReason(
  definition: ModuleDefinition,
  draft: ModuleVisibilityDraft,
): string | null {
  if (definition.required) {
    return definition.lock_reason ?? `Модуль «${definition.label}» обязателен.`;
  }
  if (
    (definition.key === "shopping" || definition.key === "equipment") &&
    draft.documents_visible
  ) {
    return "Нельзя скрыть, пока виден модуль «Документы».";
  }
  return null;
}

export default function ModuleSettingsForm() {
  const { applySavedSettings } = useModuleVisibility();
  const [saved, setSaved] = useState<ModuleSettings | null>(null);
  const [draft, setDraft] = useState<ModuleVisibilityDraft | null>(null);
  const [history, setHistory] = useState<ModuleSettingsHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [hasConflict, setHasConflict] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setHasConflict(false);
    try {
      const [settings, loadedHistory] = await Promise.all([
        getModuleSettings(),
        getModuleSettingsHistory(),
      ]);
      setSaved(settings);
      setDraft(toDraft(settings));
      setHistory(loadedHistory);
      applySavedSettings(settings);
    } catch {
      setError("Не удалось загрузить настройки модулей.");
    } finally {
      setIsLoading(false);
    }
  }, [applySavedSettings]);

  useEffect(() => {
    void load();
  }, [load]);

  const hasChanges = useMemo(
    () => Boolean(saved && draft && JSON.stringify(toDraft(saved)) !== JSON.stringify(draft)),
    [draft, saved],
  );

  function updateModule(definition: ModuleDefinition, visible: boolean) {
    if (!draft || draftLockReason(definition, draft)) return;
    const field = FIELD_BY_KEY[definition.key];
    setDraft({ ...draft, [field]: visible });
    setError(null);
    setSuccess(null);
  }

  function resetDefaults() {
    setDraft(toDraft(DEFAULT_MODULE_SETTINGS));
    setError(null);
    setSuccess("Стандартная видимость TourHub восстановлена в черновике.");
  }

  function cancelDraft() {
    if (!saved) return;
    setDraft(toDraft(saved));
    setError(null);
    setSuccess("Несохранённые изменения отменены.");
  }

  async function save() {
    if (!saved || !draft) return;
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateModuleSettings({
        ...draft,
        expected_version: saved.version,
      });
      setSaved(updated);
      setDraft(toDraft(updated));
      setHistory(await getModuleSettingsHistory());
      applySavedSettings(updated);
      setSuccess("Видимость модулей сохранена и применена без перезапуска.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError("Настройки модулей изменены в другом окне. Перезагрузите актуальную версию.");
      } else if (axios.isAxiosError(saveError)) {
        const response = saveError.response?.data as { error?: string; detail?: string } | undefined;
        setError(response?.error ?? response?.detail ?? "Не удалось сохранить настройки модулей.");
      } else {
        setError("Не удалось сохранить настройки модулей.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка настроек модулей" />
      </Box>
    );
  }

  if (!saved || !draft) {
    return <Alert severity="error">Настройки модулей недоступны.</Alert>;
  }

  const dependencyWarning =
    draft.documents_visible && (!draft.shopping_visible || !draft.equipment_visible);

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, minWidth: 0 }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Модули</Typography>
            <Typography color="text.secondary">
              Переключатели скрывают навигацию и карточки рабочего пространства. Прямые URL и API
              остаются доступными до появления ролей и backend-авторизации.
            </Typography>
          </Box>

          {error && (
            <Alert
              severity={hasConflict ? "warning" : "error"}
              action={
                hasConflict ? (
                  <Button color="inherit" size="small" onClick={() => void load()}>
                    Перезагрузить
                  </Button>
                ) : undefined
              }
            >
              {error}
            </Alert>
          )}
          {success && <Alert severity="success">{success}</Alert>}
          {dependencyWarning && (
            <Alert severity="warning">
              Видимые «Документы» требуют видимые «Закупку» и «Оборудование». Backend не сохранит
              противоречивое состояние.
            </Alert>
          )}

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "repeat(2, minmax(0, 1fr))" },
              gap: 2,
              minWidth: 0,
            }}
          >
            {saved.modules.map((definition) => {
              const field = FIELD_BY_KEY[definition.key];
              const lockReason = draftLockReason(definition, draft);
              return (
                <Paper key={definition.key} variant="outlined" sx={{ p: 2, minWidth: 0 }}>
                  <Stack spacing={1}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={draft[field]}
                          disabled={isSaving || Boolean(lockReason)}
                          onChange={(event) => updateModule(definition, event.target.checked)}
                          inputProps={{ "aria-label": definition.label }}
                        />
                      }
                      label={definition.label}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {definition.description}
                    </Typography>
                    {definition.dependencies.length > 0 && (
                      <Typography variant="caption" color="text.secondary">
                        Зависимости: {definition.dependencies.map((key) => LABEL_BY_KEY[key]).join(", ")}.
                      </Typography>
                    )}
                    {lockReason && (
                      <Typography variant="caption" color="warning.main">
                        {lockReason}
                      </Typography>
                    )}
                  </Stack>
                </Paper>
              );
            })}
          </Box>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
            <Button variant="outlined" disabled={isSaving} onClick={resetDefaults}>
              Восстановить TourHub
            </Button>
            <Button variant="outlined" disabled={isSaving || !hasChanges} onClick={cancelDraft}>
              Отменить изменения
            </Button>
            <Button
              variant="contained"
              disabled={isSaving || !hasChanges}
              onClick={() => void save()}
            >
              {isSaving ? "Сохранение…" : "Сохранить раздел"}
            </Button>
          </Stack>

          <Typography variant="caption" color="text.secondary">
            Текущая версия: {saved.version}
          </Typography>
        </Stack>
      </Paper>

      <SettingsHistoryList items={history} />
    </Stack>
  );
}
