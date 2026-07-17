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
  Typography,
} from "@mui/material";
import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  DocumentAppearanceDraft,
  DocumentAppearanceHistoryItem,
  DocumentAppearanceSettings,
  DocumentLogoSource,
  getDocumentAppearanceHistory,
  getDocumentAppearanceSettings,
  updateDocumentAppearanceSettings,
} from "../api/documentAppearanceSettingsApi";
import { ClubSettingsDetail, getSystemClubSettings } from "../api/systemSettingsApi";
import DocumentAppearancePreview from "./DocumentAppearancePreview";
import SettingsHistoryList from "./SettingsHistoryList";

const HEX_COLOR_PATTERN = /^#[0-9A-Fa-f]{6}$/;

const DEFAULT_DOCUMENT_APPEARANCE: DocumentAppearanceDraft = {
  primary_color: "#1B5E20",
  accent_color: "#F9A825",
  heading_color: "#1B5E20",
  table_header_background: "#E8F2E8",
  table_header_text: "#162018",
  table_border_color: "#405047",
  title_background_color: "#F4F7F4",
  logo_source: "main_logo",
  show_contacts: true,
  footer_text: null,
  use_document_image_as_title_background: false,
  table_density: "comfortable",
};

const COLOR_FIELDS: Array<{
  key:
    | "primary_color"
    | "accent_color"
    | "heading_color"
    | "table_header_background"
    | "table_header_text"
    | "table_border_color"
    | "title_background_color";
  label: string;
}> = [
  { key: "primary_color", label: "Основной цвет" },
  { key: "accent_color", label: "Акцентный цвет" },
  { key: "heading_color", label: "Цвет заголовков" },
  { key: "title_background_color", label: "Фон титульного блока" },
  { key: "table_header_background", label: "Фон заголовка таблицы" },
  { key: "table_header_text", label: "Текст заголовка таблицы" },
  { key: "table_border_color", label: "Границы таблицы" },
];

function toDraft(settings: DocumentAppearanceSettings): DocumentAppearanceDraft {
  return {
    primary_color: settings.primary_color,
    accent_color: settings.accent_color,
    heading_color: settings.heading_color,
    table_header_background: settings.table_header_background,
    table_header_text: settings.table_header_text,
    table_border_color: settings.table_border_color,
    title_background_color: settings.title_background_color,
    logo_source: settings.logo_source,
    show_contacts: settings.show_contacts,
    footer_text: settings.footer_text,
    use_document_image_as_title_background:
      settings.use_document_image_as_title_background,
    table_density: settings.table_density,
  };
}

function cloneDraft(draft: DocumentAppearanceDraft): DocumentAppearanceDraft {
  return { ...draft };
}

export default function DocumentAppearanceSettingsForm() {
  const [saved, setSaved] = useState<DocumentAppearanceSettings | null>(null);
  const [draft, setDraft] = useState<DocumentAppearanceDraft | null>(null);
  const [club, setClub] = useState<ClubSettingsDetail | null>(null);
  const [history, setHistory] = useState<DocumentAppearanceHistoryItem[]>([]);
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
      const [settings, clubSettings, loadedHistory] = await Promise.all([
        getDocumentAppearanceSettings(),
        getSystemClubSettings(),
        getDocumentAppearanceHistory(),
      ]);
      setSaved(settings);
      setDraft(toDraft(settings));
      setClub(clubSettings);
      setHistory(loadedHistory);
    } catch {
      setError("Не удалось загрузить настройки документов.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const hasChanges = useMemo(
    () => Boolean(saved && draft && JSON.stringify(toDraft(saved)) !== JSON.stringify(draft)),
    [draft, saved],
  );

  function update<K extends keyof DocumentAppearanceDraft>(
    key: K,
    value: DocumentAppearanceDraft[K],
  ) {
    setDraft((current) => (current ? { ...current, [key]: value } : current));
    setError(null);
    setSuccess(null);
  }

  function resetDefaults() {
    setDraft(cloneDraft(DEFAULT_DOCUMENT_APPEARANCE));
    setError(null);
    setSuccess("Стандартное оформление TourHub восстановлено в черновике.");
  }

  function cancelDraft() {
    if (!saved) return;
    setDraft(toDraft(saved));
    setError(null);
    setSuccess("Несохранённые изменения отменены.");
  }

  async function save() {
    if (!saved || !draft) return;
    const colors = COLOR_FIELDS.map(({ key }) => draft[key]);
    if (colors.some((color) => !HEX_COLOR_PATTERN.test(color))) {
      setError("Исправьте цвета: каждое значение должно иметь формат #RRGGBB.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateDocumentAppearanceSettings({
        ...cloneDraft(draft),
        footer_text: draft.footer_text?.trim() || null,
        expected_version: saved.version,
      });
      setSaved(updated);
      setDraft(toDraft(updated));
      setHistory(await getDocumentAppearanceHistory());
      setSuccess("Оформление документов сохранено. Новые файлы используют его без перезапуска.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError(
          "Настройки документов изменены в другом окне. Перезагрузите актуальную версию.",
        );
      } else if (axios.isAxiosError(saveError)) {
        const response = saveError.response?.data as { error?: string; detail?: string } | undefined;
        setError(response?.error ?? response?.detail ?? "Не удалось сохранить оформление документов.");
      } else {
        setError("Не удалось сохранить оформление документов.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка оформления документов" />
      </Box>
    );
  }

  if (!saved || !draft || !club) {
    return <Alert severity="error">Настройки документов недоступны.</Alert>;
  }

  const backgroundUnavailable =
    draft.use_document_image_as_title_background && !club.images.document_image_data_url;

  return (
    <Stack
      spacing={3}
      sx={{ width: "100%", maxWidth: "100%", minWidth: 0, overflowX: "hidden" }}
    >
      <Paper
        variant="outlined"
        sx={{
          p: { xs: 2, md: 3 },
          width: "100%",
          maxWidth: "100%",
          minWidth: 0,
          overflowX: "hidden",
        }}
      >
        <Stack spacing={2.5} sx={{ minWidth: 0 }}>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h5">Документы</Typography>
            <Typography color="text.secondary">
              Отдельное оформление PDF, Excel, печатной версии и ZIP. Настройки сайта на документы
              не переносятся автоматически.
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
          {backgroundUnavailable && (
            <Alert severity="info">
              Фоновое изображение документов ещё не загружено в разделе «Клуб». До загрузки будет
              использоваться только выбранный цвет титульного блока.
            </Alert>
          )}

          <Grid container spacing={2} sx={{ width: "100%", m: 0 }}>
            {COLOR_FIELDS.map(({ key, label }) => (
              <Grid item xs={12} sm={6} md={4} key={key} sx={{ minWidth: 0 }}>
                <TextField
                  fullWidth
                  label={label}
                  value={draft[key]}
                  disabled={isSaving}
                  error={draft[key].length > 0 && !HEX_COLOR_PATTERN.test(draft[key])}
                  helperText="Формат #RRGGBB"
                  onChange={(event) => update(key, event.target.value)}
                  InputProps={{
                    startAdornment: (
                      <Box
                        aria-hidden
                        sx={{
                          width: 22,
                          height: 22,
                          mr: 1,
                          borderRadius: 0.5,
                          border: "1px solid",
                          borderColor: "divider",
                          bgcolor: HEX_COLOR_PATTERN.test(draft[key]) ? draft[key] : "transparent",
                          flexShrink: 0,
                        }}
                      />
                    ),
                  }}
                />
              </Grid>
            ))}
          </Grid>

          <Grid container spacing={2} sx={{ width: "100%", m: 0 }}>
            <Grid item xs={12} md={6} sx={{ minWidth: 0 }}>
              <FormControl fullWidth>
                <InputLabel id="document-logo-source-label">Логотип документов</InputLabel>
                <Select
                  labelId="document-logo-source-label"
                  label="Логотип документов"
                  value={draft.logo_source}
                  disabled={isSaving}
                  onChange={(event) =>
                    update("logo_source", event.target.value as DocumentLogoSource)
                  }
                >
                  <MenuItem value="main_logo">Основной логотип</MenuItem>
                  <MenuItem value="document_image">Изображение для документов</MenuItem>
                  <MenuItem value="light_logo">Логотип светлой темы</MenuItem>
                  <MenuItem value="dark_logo">Логотип тёмной темы</MenuItem>
                  <MenuItem value="none">Без логотипа</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6} sx={{ minWidth: 0 }}>
              <FormControl fullWidth>
                <InputLabel id="document-table-density-label">Плотность таблиц</InputLabel>
                <Select
                  labelId="document-table-density-label"
                  label="Плотность таблиц"
                  value={draft.table_density}
                  disabled={isSaving}
                  onChange={(event) =>
                    update(
                      "table_density",
                      event.target.value as DocumentAppearanceDraft["table_density"],
                    )
                  }
                >
                  <MenuItem value="comfortable">Обычная</MenuItem>
                  <MenuItem value="compact">Компактная</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Stack spacing={0.5} sx={{ minWidth: 0 }}>
            <FormControlLabel
              sx={{ alignItems: "flex-start", minWidth: 0, mr: 0 }}
              control={
                <Switch
                  checked={draft.show_contacts}
                  disabled={isSaving}
                  onChange={(event) => update("show_contacts", event.target.checked)}
                />
              }
              label="Показывать контакты клуба"
            />
            <FormControlLabel
              sx={{ alignItems: "flex-start", minWidth: 0, mr: 0 }}
              control={
                <Switch
                  checked={draft.use_document_image_as_title_background}
                  disabled={isSaving}
                  onChange={(event) =>
                    update("use_document_image_as_title_background", event.target.checked)
                  }
                />
              }
              label="Использовать изображение документов как фон титульного блока"
            />
          </Stack>

          <TextField
            fullWidth
            multiline
            minRows={2}
            label="Пользовательский footer"
            value={draft.footer_text ?? ""}
            disabled={isSaving}
            inputProps={{ maxLength: 500 }}
            helperText={`${draft.footer_text?.length ?? 0}/500 · пустое поле использует стандартный footer TourHub`}
            onChange={(event) => update("footer_text", event.target.value || null)}
          />
        </Stack>
      </Paper>

      <Paper
        variant="outlined"
        sx={{
          p: { xs: 2, md: 3 },
          width: "100%",
          maxWidth: "100%",
          minWidth: 0,
          overflowX: "hidden",
        }}
      >
        <Stack spacing={2} sx={{ minWidth: 0 }}>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h6">Предпросмотр документа</Typography>
            <Typography variant="body2" color="text.secondary">
              Черновик показан только здесь. PDF, Excel и ZIP изменятся после сохранения.
            </Typography>
          </Box>
          <DocumentAppearancePreview draft={draft} club={club} />
        </Stack>
      </Paper>

      <Paper
        variant="outlined"
        sx={{ p: 2, width: "100%", maxWidth: "100%", minWidth: 0, overflowX: "hidden" }}
      >
        <Stack spacing={2} sx={{ minWidth: 0 }}>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            spacing={1}
            flexWrap="wrap"
            useFlexGap
            sx={{ minWidth: 0 }}
          >
            <Button variant="outlined" disabled={isSaving} onClick={resetDefaults}>
              Восстановить TourHub
            </Button>
            <Button
              variant="outlined"
              disabled={isSaving || !hasChanges}
              onClick={cancelDraft}
            >
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
            Сохранённая версия: {saved.version} · изменения применяются к следующей генерации.
          </Typography>
        </Stack>
      </Paper>

      <Box sx={{ minWidth: 0, overflowX: "hidden" }}>
        <SettingsHistoryList items={history} />
      </Box>
    </Stack>
  );
}
