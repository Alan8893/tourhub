import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Switch,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import axios from "axios";
import { ChangeEvent, useCallback, useEffect, useMemo, useState } from "react";

import {
  AppearanceColorTokens,
  AppearanceHistoryItem,
  AppearancePresetDefinition,
  AppearanceSettings,
  AppearanceThemeDraft,
  AppearanceThemeExport,
  DisplayModePreference,
  ResolvedDisplayMode,
  getAppearanceHistory,
  getAppearancePresets,
  getAppearanceSettings,
  updateAppearanceSettings,
} from "../api/appearanceSettingsApi";
import { DEFAULT_APPEARANCE, cloneAppearanceDraft } from "../appearance/theme";
import { useAppearance } from "../providers/AppearanceProvider";
import AppearanceColorEditor from "./AppearanceColorEditor";
import AppearancePreview from "./AppearancePreview";
import SettingsHistoryList from "./SettingsHistoryList";

const HEX_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;

function toDraft(settings: AppearanceSettings): AppearanceThemeDraft {
  return cloneAppearanceDraft({
    preset_name: settings.preset_name,
    font_family: settings.font_family,
    density: settings.density,
    border_radius: settings.border_radius,
    button_style: settings.button_style,
    card_style: settings.card_style,
    shadows_enabled: settings.shadows_enabled,
    light: settings.light,
    dark: settings.dark,
  });
}

function presetDraft(preset: AppearancePresetDefinition): AppearanceThemeDraft {
  return cloneAppearanceDraft({
    preset_name: preset.preset_name,
    font_family: preset.font_family,
    density: preset.density,
    border_radius: preset.border_radius,
    button_style: preset.button_style,
    card_style: preset.card_style,
    shadows_enabled: preset.shadows_enabled,
    light: preset.light,
    dark: preset.dark,
  });
}

function themeExport(draft: AppearanceThemeDraft): AppearanceThemeExport {
  return {
    schema: "tourhub-appearance-theme",
    schema_version: 1,
    exported_at: new Date().toISOString(),
    theme: cloneAppearanceDraft(draft),
  };
}

function parseThemeImport(value: unknown): AppearanceThemeDraft {
  if (!value || typeof value !== "object") throw new Error("Файл не содержит объект темы.");
  const candidate = value as Partial<AppearanceThemeExport>;
  if (candidate.schema !== "tourhub-appearance-theme" || candidate.schema_version !== 1) {
    throw new Error("Неподдерживаемый формат или версия файла темы.");
  }
  if (!candidate.theme || typeof candidate.theme !== "object") {
    throw new Error("В файле отсутствует раздел theme.");
  }
  return cloneAppearanceDraft({
    ...(candidate.theme as AppearanceThemeDraft),
    preset_name: "custom",
  });
}

export default function AppearanceSettingsForm() {
  const {
    displayMode,
    resolvedMode,
    setDisplayMode,
    applySavedSettings,
  } = useAppearance();
  const [saved, setSaved] = useState<AppearanceSettings | null>(null);
  const [draft, setDraft] = useState<AppearanceThemeDraft | null>(null);
  const [presets, setPresets] = useState<AppearancePresetDefinition[]>([]);
  const [history, setHistory] = useState<AppearanceHistoryItem[]>([]);
  const [previewMode, setPreviewMode] = useState<ResolvedDisplayMode>(resolvedMode);
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
      const [settings, loadedPresets, loadedHistory] = await Promise.all([
        getAppearanceSettings(),
        getAppearancePresets(),
        getAppearanceHistory(),
      ]);
      setSaved(settings);
      setDraft(toDraft(settings));
      setPresets(loadedPresets);
      setHistory(loadedHistory);
      applySavedSettings(settings);
    } catch {
      setError("Не удалось загрузить настройки оформления.");
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

  function updateScalar<K extends keyof AppearanceThemeDraft>(
    key: K,
    value: AppearanceThemeDraft[K],
  ) {
    setDraft((current) =>
      current
        ? {
            ...current,
            preset_name: key === "preset_name" ? (value as AppearanceThemeDraft["preset_name"]) : "custom",
            [key]: value,
          }
        : current,
    );
    setError(null);
    setSuccess(null);
  }

  function updateColor(
    scheme: "light" | "dark",
    key: keyof AppearanceColorTokens,
    value: string,
  ) {
    setDraft((current) =>
      current
        ? {
            ...current,
            preset_name: "custom",
            [scheme]: { ...current[scheme], [key]: value },
          }
        : current,
    );
    setError(null);
    setSuccess(null);
  }

  function applyPreset(preset: AppearancePresetDefinition) {
    setDraft(presetDraft(preset));
    setError(null);
    setSuccess(`Предустановка «${preset.label}» применена к черновику.`);
  }

  function resetDefaults() {
    const defaultPreset = presets.find((item) => item.preset_name === "tourhub");
    setDraft(defaultPreset ? presetDraft(defaultPreset) : toDraft(DEFAULT_APPEARANCE));
    setError(null);
    setSuccess("Значения TourHub восстановлены в черновике. Нажмите «Сохранить раздел».");
  }

  function cancelDraft() {
    if (!saved) return;
    setDraft(toDraft(saved));
    setError(null);
    setSuccess("Несохранённые изменения отменены.");
  }

  async function copyTheme() {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(themeExport(draft), null, 2));
      setSuccess("JSON темы скопирован в буфер обмена.");
      setError(null);
    } catch {
      setError("Не удалось скопировать тему. Используйте экспорт файла.");
    }
  }

  function exportTheme() {
    if (!draft) return;
    const blob = new Blob([JSON.stringify(themeExport(draft), null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `tourhub-theme-${new Date().toISOString().slice(0, 10)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
    setSuccess("Тема экспортирована без секретов.");
    setError(null);
  }

  async function importTheme(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text()) as unknown;
      setDraft(parseThemeImport(parsed));
      setSuccess("Тема импортирована в черновик. Проверьте preview и сохраните раздел.");
      setError(null);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "Не удалось импортировать тему.");
    }
  }

  async function save() {
    if (!saved || !draft) return;
    const colors = [...Object.values(draft.light), ...Object.values(draft.dark)];
    if (colors.some((color) => !HEX_COLOR_PATTERN.test(color))) {
      setError("Исправьте цвета: каждый токен должен иметь формат #RRGGBB.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateAppearanceSettings({
        ...cloneAppearanceDraft(draft),
        expected_version: saved.version,
      });
      setSaved(updated);
      setDraft(toDraft(updated));
      setHistory(await getAppearanceHistory());
      applySavedSettings(updated);
      setSuccess("Оформление сохранено и применено без перезапуска.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError(
          "Оформление изменено в другом окне. Перезагрузите актуальную версию перед сохранением.",
        );
      } else if (axios.isAxiosError(saveError)) {
        const response = saveError.response?.data as { error?: string } | undefined;
        setError(response?.error ?? "Не удалось сохранить оформление.");
      } else {
        setError("Не удалось сохранить оформление.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка оформления" />
      </Box>
    );
  }

  if (!saved || !draft) return <Alert severity="error">Настройки оформления недоступны.</Alert>;

  return (
    <Stack spacing={3}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Оформление</Typography>
            <Typography color="text.secondary">
              Организация задаёт обе схемы и общие токены. Каждый браузер выбирает только режим
              отображения. Произвольный CSS и внешние шрифты не используются.
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

          <FormControl fullWidth>
            <InputLabel id="display-mode-label">Личный режим отображения</InputLabel>
            <Select
              labelId="display-mode-label"
              label="Личный режим отображения"
              value={displayMode}
              onChange={(event) => setDisplayMode(event.target.value as DisplayModePreference)}
            >
              <MenuItem value="system">Как в системе</MenuItem>
              <MenuItem value="light">Светлая тема</MenuItem>
              <MenuItem value="dark">Тёмная тема</MenuItem>
            </Select>
          </FormControl>

          <Box>
            <Typography variant="h6" gutterBottom>
              Предустановки
            </Typography>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
              {presets.map((preset) => (
                <Button
                  key={preset.preset_name}
                  variant={draft.preset_name === preset.preset_name ? "contained" : "outlined"}
                  disabled={isSaving}
                  onClick={() => applyPreset(preset)}
                >
                  {preset.label}
                </Button>
              ))}
            </Stack>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel id="font-family-label">Шрифт</InputLabel>
                <Select
                  labelId="font-family-label"
                  label="Шрифт"
                  value={draft.font_family}
                  disabled={isSaving}
                  onChange={(event) =>
                    updateScalar("font_family", event.target.value as AppearanceThemeDraft["font_family"])
                  }
                >
                  <MenuItem value="system">Системный</MenuItem>
                  <MenuItem value="modern">Современный</MenuItem>
                  <MenuItem value="humanist">Гуманистический</MenuItem>
                  <MenuItem value="serif">С засечками</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel id="density-label">Плотность</InputLabel>
                <Select
                  labelId="density-label"
                  label="Плотность"
                  value={draft.density}
                  disabled={isSaving}
                  onChange={(event) =>
                    updateScalar("density", event.target.value as AppearanceThemeDraft["density"])
                  }
                >
                  <MenuItem value="comfortable">Обычная</MenuItem>
                  <MenuItem value="compact">Компактная</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Скругление, px"
                value={draft.border_radius}
                disabled={isSaving}
                inputProps={{ min: 0, max: 24 }}
                onChange={(event) =>
                  updateScalar("border_radius", Math.max(0, Math.min(24, Number(event.target.value))))
                }
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel id="button-style-label">Стиль кнопок</InputLabel>
                <Select
                  labelId="button-style-label"
                  label="Стиль кнопок"
                  value={draft.button_style}
                  disabled={isSaving}
                  onChange={(event) =>
                    updateScalar("button_style", event.target.value as AppearanceThemeDraft["button_style"])
                  }
                >
                  <MenuItem value="contained">Заливка</MenuItem>
                  <MenuItem value="soft">Мягкая заливка</MenuItem>
                  <MenuItem value="outlined">Контур</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel id="card-style-label">Стиль карточек</InputLabel>
                <Select
                  labelId="card-style-label"
                  label="Стиль карточек"
                  value={draft.card_style}
                  disabled={isSaving}
                  onChange={(event) =>
                    updateScalar("card_style", event.target.value as AppearanceThemeDraft["card_style"])
                  }
                >
                  <MenuItem value="outlined">Контур</MenuItem>
                  <MenuItem value="elevated">С тенью</MenuItem>
                  <MenuItem value="flat">Плоские</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={draft.shadows_enabled}
                    disabled={isSaving}
                    onChange={(event) => updateScalar("shadows_enabled", event.target.checked)}
                  />
                }
                label="Использовать тени"
              />
            </Grid>
          </Grid>
        </Stack>
      </Paper>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "stretch", sm: "center" }}
            spacing={1}
          >
            <Box>
              <Typography variant="h6">Живой предпросмотр</Typography>
              <Typography variant="body2" color="text.secondary">
                Черновик применяется только внутри этой панели до сохранения.
              </Typography>
            </Box>
            <ToggleButtonGroup
              exclusive
              size="small"
              value={previewMode}
              onChange={(_, value: ResolvedDisplayMode | null) => value && setPreviewMode(value)}
              aria-label="Режим предпросмотра"
            >
              <ToggleButton value="light">Светлая</ToggleButton>
              <ToggleButton value="dark">Тёмная</ToggleButton>
            </ToggleButtonGroup>
          </Stack>
          <AppearancePreview draft={draft} mode={previewMode} />
        </Stack>
      </Paper>

      <AppearanceColorEditor
        title="Светлая тема"
        tokens={draft.light}
        disabled={isSaving}
        onChange={(key, value) => updateColor("light", key, value)}
      />
      <AppearanceColorEditor
        title="Тёмная тема"
        tokens={draft.dark}
        disabled={isSaving}
        onChange={(key, value) => updateColor("dark", key, value)}
      />

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Stack spacing={2}>
          <Typography variant="h6">Действия с темой</Typography>
          <Typography variant="body2" color="text.secondary">
            Theme JSON содержит только параметры оформления. Секретов и данных клуба в нём нет.
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
            <Button variant="outlined" disabled={isSaving} onClick={resetDefaults}>
              Восстановить TourHub
            </Button>
            <Button variant="outlined" disabled={isSaving || !hasChanges} onClick={cancelDraft}>
              Отменить изменения
            </Button>
            <Button variant="outlined" disabled={isSaving} onClick={() => void copyTheme()}>
              Скопировать JSON
            </Button>
            <Button variant="outlined" disabled={isSaving} onClick={exportTheme}>
              Экспортировать тему
            </Button>
            <Button component="label" variant="outlined" disabled={isSaving}>
              Импортировать тему
              <input hidden type="file" accept="application/json,.json" onChange={importTheme} />
            </Button>
          </Stack>
        </Stack>
      </Paper>

      <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
        <Button disabled={isSaving || !hasChanges} onClick={() => void save()}>
          {isSaving ? "Сохранение…" : "Сохранить раздел"}
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ alignSelf: "center" }}>
          Сохранённая версия: {saved.version}. Текущий режим: {resolvedMode === "dark" ? "тёмный" : "светлый"}.
        </Typography>
      </Stack>

      <SettingsHistoryList items={history} />
    </Stack>
  );
}
