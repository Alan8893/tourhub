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
import { checkTransport, sendTestTransport } from "../api/transportActions";
import SettingsHistoryList from "./SettingsHistoryList";

interface EditorDraft {
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

function toDraft(settings: MailSettings): EditorDraft {
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
  return value.trim() || null;
}

function errorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || fallback;
  }
  return fallback;
}

export default function MailSettingsWorkspace() {
  const [saved, setSaved] = useState<MailSettings | null>(null);
  const [draft, setDraft] = useState<EditorDraft | null>(null);
  const [history, setHistory] = useState<MailSettingsHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [busyAction, setBusyAction] = useState<"save" | "check" | "test" | null>(null);
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

  function patchDraft(patch: Partial<EditorDraft>) {
    if (!draft) return;
    setDraft({ ...draft, ...patch });
    setError(null);
    setSuccess(null);
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

    setBusyAction("save");
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
      setSuccess("Настройки почты сохранены. Теперь можно проверить соединение.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError("Настройки изменены в другом окне. Перезагрузите актуальную версию.");
      } else {
        setError(errorMessage(saveError, "Не удалось сохранить настройки почты."));
      }
    } finally {
      setBusyAction(null);
    }
  }

  async function runAction(kind: "check" | "test") {
    setBusyAction(kind);
    setError(null);
    setSuccess(null);
    try {
      const result = kind === "check" ? await checkTransport() : await sendTestTransport();
      const suffix = result.recipient ? ` Получатель: ${result.recipient}.` : "";
      setSuccess(`${result.message} Попыток: ${result.attempts}.${suffix}`);
    } catch (actionError) {
      setError(errorMessage(actionError, "Почтовая операция не выполнена."));
    } finally {
      setBusyAction(null);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка настроек почты" />
      </Box>
    );
  }
  if (!saved || !draft) return <Alert severity="error">Настройки почты недоступны.</Alert>;

  const disabled = busyAction !== null;
  const actionBlocked = disabled || hasChanges;

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, minWidth: 0 }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Почта</Typography>
            <Typography color="text.secondary">
              Сохраните параметры подключения, проверьте соединение и отправьте фиксированное тестовое письмо.
            </Typography>
          </Box>

          <Alert severity="info">
            Значение для SMTP-аутентификации задаётся оператором через {saved.secret_environment_variable} и не вводится в TourHub.
          </Alert>
          {error && (
            <Alert
              severity={hasConflict ? "warning" : "error"}
              action={hasConflict ? <Button color="inherit" onClick={() => void load()}>Перезагрузить</Button> : undefined}
            >
              {error}
            </Alert>
          )}
          {success && <Alert severity="success">{success}</Alert>}

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Chip
              color={saved.delivery_available ? "success" : "default"}
              label={saved.delivery_available ? "Конфигурация готова" : "Не хватает значения окружения"}
            />
            <Chip
              color={saved.test_delivery_available ? "success" : "default"}
              label={saved.test_delivery_available ? "Тестовый адрес задан" : "Тестовый адрес не задан"}
            />
          </Stack>

          <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(2, minmax(0, 1fr))" }, gap: 2 }}>
            <TextField label="SMTP host" value={draft.smtpHost} onChange={(event) => patchDraft({ smtpHost: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="SMTP-порт" type="number" value={draft.smtpPort} onChange={(event) => patchDraft({ smtpPort: event.target.value })} disabled={disabled} fullWidth />
            <FormControl fullWidth disabled={disabled}>
              <InputLabel id="mail-security-mode-label">Защита соединения</InputLabel>
              <Select labelId="mail-security-mode-label" label="Защита соединения" value={draft.securityMode} onChange={(event) => patchDraft({ securityMode: event.target.value as MailSecurityMode })}>
                <MenuItem value="plain">Без шифрования</MenuItem>
                <MenuItem value="starttls">STARTTLS</MenuItem>
                <MenuItem value="tls">TLS с момента подключения</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Имя пользователя SMTP" value={draft.smtpUsername} onChange={(event) => patchDraft({ smtpUsername: event.target.value })} helperText="Необязательно для серверов без аутентификации." disabled={disabled} fullWidth />
            <TextField label="Адрес отправителя" value={draft.senderEmail} onChange={(event) => patchDraft({ senderEmail: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="Имя отправителя" value={draft.senderName} onChange={(event) => patchDraft({ senderName: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="Reply-To" value={draft.replyToEmail} onChange={(event) => patchDraft({ replyToEmail: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="Тестовый адрес" type="email" value={draft.testRecipientEmail} onChange={(event) => patchDraft({ testRecipientEmail: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="Тайм-аут, секунд" type="number" value={draft.timeoutSeconds} onChange={(event) => patchDraft({ timeoutSeconds: event.target.value })} disabled={disabled} fullWidth />
            <TextField label="Повторные попытки" type="number" value={draft.retryCount} onChange={(event) => patchDraft({ retryCount: event.target.value })} disabled={disabled} fullWidth />
          </Box>

          {hasChanges && <Alert severity="warning">Сначала сохраните изменения, затем проверяйте соединение.</Alert>}

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} flexWrap="wrap" useFlexGap>
            <Button variant="outlined" disabled={disabled} onClick={() => setDraft(toDraft(DEFAULT_MAIL_SETTINGS))}>Восстановить TourHub</Button>
            <Button variant="outlined" disabled={disabled || !hasChanges} onClick={() => setDraft(toDraft(saved))}>Отменить изменения</Button>
            <Button variant="contained" disabled={disabled || !hasChanges} onClick={() => void save()}>{busyAction === "save" ? "Сохранение…" : "Сохранить раздел"}</Button>
            <Button variant="outlined" disabled={actionBlocked || !saved.delivery_available} onClick={() => void runAction("check")}>{busyAction === "check" ? "Проверка…" : "Проверить соединение"}</Button>
            <Button variant="outlined" disabled={actionBlocked || !saved.test_delivery_available} onClick={() => void runAction("test")}>{busyAction === "test" ? "Отправка…" : "Отправить тестовое письмо"}</Button>
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Проверка и отправка используют только сохранённую версию {saved.version}. Значения окружения не отображаются и не сохраняются в приложении.
          </Typography>
        </Stack>
      </Paper>
      <SettingsHistoryList items={history} />
    </Stack>
  );
}
