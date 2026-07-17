import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { useCallback, useEffect, useMemo, useState } from "react";

import {
  DEFAULT_MAIL_SETTINGS,
  MailSecurityMode,
  MailSettings,
  MailSettingsHistoryItem,
  getMailSettings,
  getMailSettingsHistory,
  updateMailSettings,
} from "../api/mailSettingsApi";
import SettingsHistoryList from "./SettingsHistoryList";

interface MailEditorDraft {
  smtpHost: string;
  smtpPort: string;
  securityMode: MailSecurityMode;
  smtpUsername: string;
  senderEmail: string;
  senderName: string;
  replyToEmail: string;
  testRecipientEmail: string;
  timeoutSeconds: string;
  retryCount: string;
}

interface ApiErrorBody {
  error?: string;
  detail?: string;
  details?: Array<{ msg?: string }>;
}

function toDraft(settings: MailSettings): MailEditorDraft {
  return {
    smtpHost: settings.smtp_host,
    smtpPort: String(settings.smtp_port),
    securityMode: settings.security_mode,
    smtpUsername: settings.smtp_username ?? "",
    senderEmail: settings.sender_email,
    senderName: settings.sender_name,
    replyToEmail: settings.reply_to_email ?? "",
    testRecipientEmail: settings.test_recipient_email ?? "",
    timeoutSeconds: String(settings.timeout_seconds),
    retryCount: String(settings.retry_count),
  };
}

function optionalText(value: string): string | null {
  const normalized = value.trim();
  return normalized || null;
}

function apiErrorMessage(body: ApiErrorBody | undefined): string {
  const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
  return details || body?.detail || body?.error || "Не удалось сохранить настройки почты.";
}

function securityLabel(mode: MailSecurityMode): string {
  if (mode === "tls") return "TLS с момента подключения";
  if (mode === "starttls") return "STARTTLS";
  return "Без шифрования";
}

export default function MailSettingsForm() {
  const [saved, setSaved] = useState<MailSettings | null>(null);
  const [draft, setDraft] = useState<MailEditorDraft | null>(null);
  const [history, setHistory] = useState<MailSettingsHistoryItem[]>([]);
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
        getMailSettings(),
        getMailSettingsHistory(),
      ]);
      setSaved(settings);
      setDraft(toDraft(settings));
      setHistory(loadedHistory);
    } catch {
      setError("Не удалось загрузить настройки почты.");
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

  function patchDraft(patch: Partial<MailEditorDraft>) {
    if (!draft) return;
    setDraft({ ...draft, ...patch });
    setError(null);
    setSuccess(null);
  }

  function resetDefaults() {
    setDraft(toDraft(DEFAULT_MAIL_SETTINGS));
    setError(null);
    setSuccess("Стандартная SMTP-конфигурация TourHub восстановлена в черновике.");
  }

  function cancelDraft() {
    if (!saved) return;
    setDraft(toDraft(saved));
    setError(null);
    setSuccess("Несохранённые изменения отменены.");
  }

  async function save() {
    if (!saved || !draft) return;

    const smtpPort = Number(draft.smtpPort);
    const timeoutSeconds = Number(draft.timeoutSeconds);
    const retryCount = Number(draft.retryCount);

    if (!Number.isInteger(smtpPort) || smtpPort < 1 || smtpPort > 65535) {
      setError("SMTP-порт должен быть целым числом от 1 до 65535.");
      return;
    }
    if (!Number.isInteger(timeoutSeconds) || timeoutSeconds < 1 || timeoutSeconds > 120) {
      setError("Тайм-аут должен быть целым числом от 1 до 120 секунд.");
      return;
    }
    if (!Number.isInteger(retryCount) || retryCount < 0 || retryCount > 10) {
      setError("Количество повторных попыток должно быть целым числом от 0 до 10.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateMailSettings({
        expected_version: saved.version,
        smtp_host: draft.smtpHost,
        smtp_port: smtpPort,
        security_mode: draft.securityMode,
        smtp_username: optionalText(draft.smtpUsername),
        sender_email: draft.senderEmail,
        sender_name: draft.senderName,
        reply_to_email: optionalText(draft.replyToEmail),
        test_recipient_email: optionalText(draft.testRecipientEmail),
        timeout_seconds: timeoutSeconds,
        retry_count: retryCount,
      });
      setSaved(updated);
      setDraft(toDraft(updated));
      setHistory(await getMailSettingsHistory());
      setSuccess("Несекретные настройки почты сохранены. Доставка останется выключенной до реализации доступа.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError("Настройки почты изменены в другом окне. Перезагрузите актуальную версию.");
      } else if (axios.isAxiosError(saveError)) {
        setError(apiErrorMessage(saveError.response?.data as ApiErrorBody | undefined));
      } else {
        setError("Не удалось сохранить настройки почты.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка настроек почты" />
      </Box>
    );
  }

  if (!saved || !draft) {
    return <Alert severity="error">Настройки почты недоступны.</Alert>;
  }

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, minWidth: 0 }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Почта</Typography>
            <Typography color="text.secondary">
              Здесь сохраняются только несекретные параметры будущей SMTP-доставки. TourHub пока не
              подключается к почтовому серверу и не отправляет сообщения.
            </Typography>
          </Box>

          <Alert severity="info">
            Рабочая доставка и фиксированное русское тестовое письмо появятся после Access
            foundation. Сохранение этого раздела не проверяет соединение и учётные данные.
          </Alert>

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

          <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
            <Stack spacing={1}>
              <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems={{ sm: "center" }}>
                <Typography variant="subtitle1">Внешний SMTP-секрет</Typography>
                <Chip
                  size="small"
                  color={saved.secret_configured ? "success" : "default"}
                  label={saved.secret_configured ? "Настроен в environment" : "Не настроен"}
                />
              </Stack>
              <Typography variant="body2" color="text.secondary">
                Значение задаётся оператором через {saved.secret_environment_variable}. Оно не
                вводится на этой странице, не хранится в PostgreSQL и не возвращается API.
              </Typography>
            </Stack>
          </Paper>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "repeat(2, minmax(0, 1fr))" },
              gap: 2,
              minWidth: 0,
            }}
          >
            <TextField
              label="SMTP host"
              value={draft.smtpHost}
              onChange={(event) => patchDraft({ smtpHost: event.target.value })}
              helperText="DNS-имя, IP-адрес или localhost; без протокола и порта."
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="SMTP-порт"
              type="number"
              value={draft.smtpPort}
              onChange={(event) => patchDraft({ smtpPort: event.target.value })}
              inputProps={{ min: 1, max: 65535, step: 1 }}
              disabled={isSaving}
              fullWidth
            />
            <FormControl fullWidth disabled={isSaving}>
              <InputLabel id="mail-security-mode-label">Защита соединения</InputLabel>
              <Select
                labelId="mail-security-mode-label"
                label="Защита соединения"
                value={draft.securityMode}
                onChange={(event) =>
                  patchDraft({ securityMode: event.target.value as MailSecurityMode })
                }
              >
                <MenuItem value="plain">Без шифрования</MenuItem>
                <MenuItem value="starttls">STARTTLS</MenuItem>
                <MenuItem value="tls">TLS с момента подключения</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Имя пользователя SMTP"
              value={draft.smtpUsername}
              onChange={(event) => patchDraft({ smtpUsername: event.target.value })}
              helperText="Необязательно. Секрет хранится отдельно."
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Адрес отправителя"
              value={draft.senderEmail}
              onChange={(event) => patchDraft({ senderEmail: event.target.value })}
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Имя отправителя"
              value={draft.senderName}
              onChange={(event) => patchDraft({ senderName: event.target.value })}
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Reply-To"
              value={draft.replyToEmail}
              onChange={(event) => patchDraft({ replyToEmail: event.target.value })}
              helperText="Необязательно."
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Тестовый адрес"
              value={draft.testRecipientEmail}
              onChange={(event) => patchDraft({ testRecipientEmail: event.target.value })}
              helperText="Будущий получатель фиксированного русского тестового письма."
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Тайм-аут, секунд"
              type="number"
              value={draft.timeoutSeconds}
              onChange={(event) => patchDraft({ timeoutSeconds: event.target.value })}
              inputProps={{ min: 1, max: 120, step: 1 }}
              disabled={isSaving}
              fullWidth
            />
            <TextField
              label="Повторные попытки"
              type="number"
              value={draft.retryCount}
              onChange={(event) => patchDraft({ retryCount: event.target.value })}
              inputProps={{ min: 0, max: 10, step: 1 }}
              disabled={isSaving}
              fullWidth
            />
          </Box>

          <Paper variant="outlined" sx={{ p: 2, bgcolor: "action.hover", minWidth: 0 }}>
            <Typography variant="subtitle2">Сводка будущего подключения</Typography>
            <Typography variant="body2" color="text.secondary">
              {draft.smtpHost || "—"}:{draft.smtpPort || "—"} · {securityLabel(draft.securityMode)} ·
              отправитель {draft.senderName || "—"} &lt;{draft.senderEmail || "—"}&gt; · тайм-аут
              {" "}{draft.timeoutSeconds || "—"} сек. · попыток {draft.retryCount || "0"}.
            </Typography>
          </Paper>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
            <Button variant="outlined" disabled={isSaving} onClick={resetDefaults}>
              Восстановить TourHub
            </Button>
            <Button variant="outlined" disabled={isSaving || !hasChanges} onClick={cancelDraft}>
              Отменить изменения
            </Button>
            <Button variant="contained" disabled={isSaving || !hasChanges} onClick={() => void save()}>
              {isSaving ? "Сохранение…" : "Сохранить раздел"}
            </Button>
            <Button variant="outlined" disabled>
              Отправить тестовое письмо
            </Button>
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Тестовая отправка недоступна до реализации пользователей, доступа и рабочего mail
            delivery. Текущая версия: {saved.version}.
          </Typography>
        </Stack>
      </Paper>
      <SettingsHistoryList items={history} />
    </Stack>
  );
}
