import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  ClubImageKey,
  ClubImageUpdate,
  ClubSettingsDetail,
  ClubSettingsUpdate,
  getSystemClubSettings,
  getSystemSettingsHistory,
  SystemSettingsHistoryItem,
  updateSystemClubSettings,
} from "../api/systemSettingsApi";
import ImageSettingField from "./ImageSettingField";
import SettingsHistoryList from "./SettingsHistoryList";

const IMAGE_RESPONSE_KEYS: Record<ClubImageKey, keyof ClubSettingsDetail["images"]> = {
  main_logo: "main_logo_data_url",
  light_logo: "light_logo_data_url",
  dark_logo: "dark_logo_data_url",
  square_icon: "square_icon_data_url",
  favicon: "favicon_data_url",
  login_background: "login_background_data_url",
  document_image: "document_image_data_url",
};

const IMAGE_FIELDS: Array<{
  key: ClubImageKey;
  label: string;
  description: string;
  maxBytes: number;
}> = [
  {
    key: "main_logo",
    label: "Основной логотип",
    description: "Используется как fallback и продолжает брендировать существующие документы.",
    maxBytes: 2_000_000,
  },
  {
    key: "light_logo",
    label: "Логотип для светлой темы",
    description: "Если не задан, будет использоваться основной логотип.",
    maxBytes: 2_000_000,
  },
  {
    key: "dark_logo",
    label: "Логотип для тёмной темы",
    description: "Если не задан, будет использоваться основной логотип.",
    maxBytes: 2_000_000,
  },
  {
    key: "square_icon",
    label: "Квадратная иконка",
    description: "Подготовлена для компактной навигации и будущего экрана входа.",
    maxBytes: 512_000,
  },
  {
    key: "favicon",
    label: "Favicon",
    description: "Применяется к вкладке браузера после сохранения.",
    maxBytes: 512_000,
  },
  {
    key: "login_background",
    label: "Фон страницы входа",
    description: "Сохраняется сейчас и будет использован после реализации доступа.",
    maxBytes: 5_000_000,
  },
  {
    key: "document_image",
    label: "Изображение для документов",
    description: "Подготовлено для отдельного оформления PDF, Excel и печати.",
    maxBytes: 5_000_000,
  },
];

function cloneSettings(settings: ClubSettingsDetail): ClubSettingsDetail {
  return {
    ...settings,
    social_links: settings.social_links.map((link) => ({ ...link })),
    images: { ...settings.images },
  };
}

function optionalValue(value: string | null): string | null {
  const normalized = value?.trim() ?? "";
  return normalized || null;
}

function applyFavicon(settings: ClubSettingsDetail) {
  const favicon =
    settings.images.favicon_data_url ??
    settings.images.square_icon_data_url ??
    settings.images.main_logo_data_url;
  if (!favicon) return;

  let element = document.querySelector<HTMLLinkElement>('link[rel="icon"]');
  if (!element) {
    element = document.createElement("link");
    element.rel = "icon";
    document.head.appendChild(element);
  }
  element.href = favicon;
}

export default function ClubSettingsForm() {
  const [settings, setSettings] = useState<ClubSettingsDetail | null>(null);
  const [draft, setDraft] = useState<ClubSettingsDetail | null>(null);
  const [imageUpdates, setImageUpdates] = useState<
    Partial<Record<ClubImageKey, ClubImageUpdate>>
  >({});
  const [history, setHistory] = useState<SystemSettingsHistoryItem[]>([]);
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
      const [loadedSettings, loadedHistory] = await Promise.all([
        getSystemClubSettings(),
        getSystemSettingsHistory(),
      ]);
      setSettings(loadedSettings);
      setDraft(cloneSettings(loadedSettings));
      setImageUpdates({});
      setHistory(loadedHistory);
      applyFavicon(loadedSettings);
    } catch {
      setError("Не удалось загрузить настройки системы.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const imagePreviews = useMemo(() => {
    if (!draft) return {} as Record<ClubImageKey, string | null>;
    return Object.fromEntries(
      IMAGE_FIELDS.map(({ key }) => {
        const update = imageUpdates[key];
        if (update?.remove) return [key, null];
        if (update?.data_url) return [key, update.data_url];
        return [key, draft.images[IMAGE_RESPONSE_KEYS[key]]];
      }),
    ) as Record<ClubImageKey, string | null>;
  }, [draft, imageUpdates]);

  function updateField(
    field:
      | "club_name"
      | "short_name"
      | "legal_name"
      | "description"
      | "address"
      | "phone"
      | "email"
      | "website"
      | "timezone"
      | "city"
      | "region",
    value: string,
  ) {
    setDraft((current) => (current ? { ...current, [field]: value } : current));
    setSuccess(null);
  }

  function updateSocialLink(index: number, field: "label" | "url", value: string) {
    setDraft((current) => {
      if (!current) return current;
      const socialLinks = current.social_links.map((link, linkIndex) =>
        linkIndex === index ? { ...link, [field]: value } : link,
      );
      return { ...current, social_links: socialLinks };
    });
    setSuccess(null);
  }

  function addSocialLink() {
    setDraft((current) => {
      if (!current || current.social_links.length >= 10) return current;
      return {
        ...current,
        social_links: [...current.social_links, { label: "", url: "" }],
      };
    });
  }

  function removeSocialLink(index: number) {
    setDraft((current) =>
      current
        ? {
            ...current,
            social_links: current.social_links.filter((_, linkIndex) => linkIndex !== index),
          }
        : current,
    );
  }

  function uploadImage(key: ClubImageKey, dataUrl: string) {
    setImageUpdates((current) => ({
      ...current,
      [key]: { data_url: dataUrl, remove: false },
    }));
    setSuccess(null);
  }

  function removeImage(key: ClubImageKey) {
    setImageUpdates((current) => ({
      ...current,
      [key]: { data_url: null, remove: true },
    }));
    setSuccess(null);
  }

  async function handleSave() {
    if (!draft || !settings) return;
    const clubName = draft.club_name.trim();
    if (!clubName) {
      setError("Название клуба — единственное обязательное поле.");
      return;
    }

    const socialLinks = draft.social_links
      .map((link) => ({ label: link.label.trim(), url: link.url.trim() }))
      .filter((link) => link.label || link.url);
    if (socialLinks.some((link) => !link.label || !link.url)) {
      setError("Для каждой социальной сети укажите и название, и ссылку.");
      return;
    }

    const payload: ClubSettingsUpdate = {
      expected_version: settings.version,
      club_name: clubName,
      short_name: optionalValue(draft.short_name),
      legal_name: optionalValue(draft.legal_name),
      description: optionalValue(draft.description),
      address: optionalValue(draft.address),
      phone: optionalValue(draft.phone),
      email: optionalValue(draft.email),
      website: optionalValue(draft.website),
      timezone: optionalValue(draft.timezone),
      city: optionalValue(draft.city),
      region: optionalValue(draft.region),
      social_links: socialLinks,
      images: imageUpdates,
    };

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateSystemClubSettings(payload);
      setSettings(updated);
      setDraft(cloneSettings(updated));
      setImageUpdates({});
      setHistory(await getSystemSettingsHistory());
      applyFavicon(updated);
      setSuccess("Настройки клуба сохранены.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError(
          "Настройки уже были изменены в другом окне. Перезагрузите актуальную версию перед повторным сохранением.",
        );
      } else if (axios.isAxiosError(saveError)) {
        const detail = (saveError.response?.data as { detail?: string } | undefined)?.detail;
        setError(detail ?? "Не удалось сохранить настройки клуба.");
      } else {
        setError("Не удалось сохранить настройки клуба.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка настроек" />
      </Box>
    );
  }

  if (!draft || !settings) {
    return <Alert severity="error">Настройки клуба недоступны.</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Клуб</Typography>
            <Typography color="text.secondary">
              Название клуба обязательно. Остальные сведения можно заполнять по мере готовности.
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

          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                required
                label="Название клуба"
                value={draft.club_name}
                disabled={isSaving}
                inputProps={{ maxLength: 255 }}
                onChange={(event) => updateField("club_name", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Краткое название"
                value={draft.short_name ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 100 }}
                onChange={(event) => updateField("short_name", event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Полное официальное название"
                value={draft.legal_name ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 255 }}
                onChange={(event) => updateField("legal_name", event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                minRows={3}
                label="Описание клуба"
                value={draft.description ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 5000 }}
                onChange={(event) => updateField("description", event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                minRows={2}
                label="Адрес"
                value={draft.address ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 500 }}
                onChange={(event) => updateField("address", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Город"
                value={draft.city ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 255 }}
                onChange={(event) => updateField("city", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Регион"
                value={draft.region ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 255 }}
                onChange={(event) => updateField("region", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Телефон"
                value={draft.phone ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 100 }}
                onChange={(event) => updateField("phone", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="email"
                label="Email"
                value={draft.email ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 320 }}
                onChange={(event) => updateField("email", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="url"
                label="Сайт"
                placeholder="https://example.org"
                value={draft.website ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 500 }}
                onChange={(event) => updateField("website", event.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Часовой пояс"
                placeholder="Europe/Moscow"
                value={draft.timezone ?? ""}
                disabled={isSaving}
                inputProps={{ maxLength: 64 }}
                onChange={(event) => updateField("timezone", event.target.value)}
                helperText="Используйте название часового пояса IANA."
              />
            </Grid>
          </Grid>

          <Divider />

          <Stack spacing={1.5}>
            <Box>
              <Typography variant="h6">Социальные сети</Typography>
              <Typography variant="body2" color="text.secondary">
                Можно добавить до 10 подписанных ссылок.
              </Typography>
            </Box>
            {draft.social_links.map((link, index) => (
              <Grid container spacing={1} key={`${index}-${link.label}`}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Название"
                    value={link.label}
                    disabled={isSaving}
                    inputProps={{ maxLength: 80 }}
                    onChange={(event) => updateSocialLink(index, "label", event.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="url"
                    label="Ссылка"
                    placeholder="https://"
                    value={link.url}
                    disabled={isSaving}
                    inputProps={{ maxLength: 500 }}
                    onChange={(event) => updateSocialLink(index, "url", event.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <Button
                    fullWidth
                    sx={{ height: "100%" }}
                    disabled={isSaving}
                    onClick={() => removeSocialLink(index)}
                  >
                    Удалить
                  </Button>
                </Grid>
              </Grid>
            ))}
            <Button
              variant="outlined"
              sx={{ alignSelf: "flex-start" }}
              disabled={isSaving || draft.social_links.length >= 10}
              onClick={addSocialLink}
            >
              Добавить ссылку
            </Button>
          </Stack>

          <Divider />

          <Box>
            <Typography variant="h6">Изображения клуба</Typography>
            <Typography variant="body2" color="text.secondary">
              SVG не принимается. Светлый и тёмный логотипы используют основной логотип как
              fallback.
            </Typography>
          </Box>

          <Grid container spacing={2}>
            {IMAGE_FIELDS.map((field) => (
              <Grid item xs={12} lg={6} key={field.key}>
                <ImageSettingField
                  label={field.label}
                  description={field.description}
                  preview={imagePreviews[field.key]}
                  maxBytes={field.maxBytes}
                  disabled={isSaving}
                  onUpload={(dataUrl) => uploadImage(field.key, dataUrl)}
                  onRemove={() => removeImage(field.key)}
                />
              </Grid>
            ))}
          </Grid>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems="flex-start">
            <Button variant="contained" disabled={isSaving} onClick={() => void handleSave()}>
              {isSaving ? "Сохранение…" : "Сохранить раздел"}
            </Button>
            <Button disabled={isSaving} onClick={() => void load()}>
              Восстановить сохранённые значения
            </Button>
          </Stack>

          <Typography variant="caption" color="text.secondary">
            Текущая версия: {settings.version}. Обновлено:{" "}
            {new Date(settings.updated_at).toLocaleString("ru-RU")}.
          </Typography>
        </Stack>
      </Paper>

      <SettingsHistoryList items={history} />
    </Stack>
  );
}
