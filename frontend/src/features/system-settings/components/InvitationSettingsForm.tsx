import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
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
  DEFAULT_INVITATION_SETTINGS,
  InvitationDefaultRole,
  InvitationSettings,
  InvitationSettingsHistoryItem,
  getInvitationSettings,
  getInvitationSettingsHistory,
  updateInvitationSettings,
} from "../api/invitationSettingsApi";
import SettingsHistoryList from "./SettingsHistoryList";

interface InvitationEditorDraft {
  expiresAfterDays: string;
  defaultRole: InvitationDefaultRole;
  allowedDomainsText: string;
  allowResend: boolean;
  activeInvitationLimit: string;
  administratorsOnly: boolean;
  requireEmailConfirmation: boolean;
}

function toDraft(settings: InvitationSettings): InvitationEditorDraft {
  return {
    expiresAfterDays: String(settings.expires_after_days),
    defaultRole: settings.default_role,
    allowedDomainsText: settings.allowed_email_domains.join("\n"),
    allowResend: settings.allow_resend,
    activeInvitationLimit: String(settings.active_invitation_limit),
    administratorsOnly: settings.administrators_only,
    requireEmailConfirmation: settings.require_email_confirmation,
  };
}

function parseDomains(value: string): string[] {
  return value
    .split(/[\n,;]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function roleLabel(role: InvitationDefaultRole): string {
  return role === "verified_instructor" ? "Проверенный инструктор" : "Инструктор";
}

export default function InvitationSettingsForm() {
  const [saved, setSaved] = useState<InvitationSettings | null>(null);
  const [draft, setDraft] = useState<InvitationEditorDraft | null>(null);
  const [history, setHistory] = useState<InvitationSettingsHistoryItem[]>([]);
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
        getInvitationSettings(),
        getInvitationSettingsHistory(),
      ]);
      setSaved(settings);
      setDraft(toDraft(settings));
      setHistory(loadedHistory);
    } catch {
      setError("Не удалось загрузить политику приглашений.");
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

  function updateDraft(patch: Partial<InvitationEditorDraft>) {
    if (!draft) return;
    setDraft({ ...draft, ...patch });
    setError(null);
    setSuccess(null);
  }

  function resetDefaults() {
    setDraft(toDraft(DEFAULT_INVITATION_SETTINGS));
    setError(null);
    setSuccess("Стандартная политика TourHub восстановлена в черновике.");
  }

  function cancelDraft() {
    if (!saved) return;
    setDraft(toDraft(saved));
    setError(null);
    setSuccess("Несохранённые изменения отменены.");
  }

  async function save() {
    if (!saved || !draft) return;
    const expiresAfterDays = Number(draft.expiresAfterDays);
    const activeInvitationLimit = Number(draft.activeInvitationLimit);
    if (!Number.isInteger(expiresAfterDays) || expiresAfterDays < 1 || expiresAfterDays > 90) {
      setError("Срок действия должен быть целым числом от 1 до 90 дней.");
      return;
    }
    if (
      !Number.isInteger(activeInvitationLimit) ||
      activeInvitationLimit < 1 ||
      activeInvitationLimit > 1000
    ) {
      setError("Лимит активных приглашений должен быть целым числом от 1 до 1000.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    setHasConflict(false);
    try {
      const updated = await updateInvitationSettings({
        expected_version: saved.version,
        expires_after_days: expiresAfterDays,
        default_role: draft.defaultRole,
        allowed_email_domains: parseDomains(draft.allowedDomainsText),
        allow_resend: draft.allowResend,
        active_invitation_limit: activeInvitationLimit,
        administrators_only: true,
        require_email_confirmation: draft.requireEmailConfirmation,
      });
      setSaved(updated);
      setDraft(toDraft(updated));
      setHistory(await getInvitationSettingsHistory());
      setSuccess("Политика приглашений сохранена. Она будет применяться после реализации доступа.");
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setHasConflict(true);
        setError("Политика приглашений изменена в другом окне. Перезагрузите актуальную версию.");
      } else if (axios.isAxiosError(saveError)) {
        const response = saveError.response?.data as { error?: string; detail?: string } | undefined;
        setError(response?.error ?? response?.detail ?? "Не удалось сохранить политику приглашений.");
      } else {
        setError("Не удалось сохранить политику приглашений.");
      }
    } finally {
      setIsSaving(false);
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка политики приглашений" />
      </Box>
    );
  }

  if (!saved || !draft) {
    return <Alert severity="error">Политика приглашений недоступна.</Alert>;
  }

  const domainCount = parseDomains(draft.allowedDomainsText).length;

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, minWidth: 0 }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Приглашения</Typography>
            <Typography color="text.secondary">
              Эти правила подготовлены для будущего многопользовательского режима. Сейчас TourHub не
              создаёт приглашения, пользователей, токены и письма.
            </Typography>
          </Box>

          <Alert severity="info">
            Рабочий список приглашений, отправка и принятие появятся в Access foundation. Сохранённая
            здесь политика станет backend-источником правил для той реализации.
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

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "repeat(2, minmax(0, 1fr))" },
              gap: 2,
              minWidth: 0,
            }}
          >
            <TextField
              label="Срок действия, дней"
              type="number"
              value={draft.expiresAfterDays}
              onChange={(event) => updateDraft({ expiresAfterDays: event.target.value })}
              inputProps={{ min: 1, max: 90, step: 1 }}
              helperText="От 1 до 90 дней."
              disabled={isSaving}
              fullWidth
            />

            <FormControl fullWidth disabled={isSaving}>
              <InputLabel id="invitation-default-role-label">Роль по умолчанию</InputLabel>
              <Select
                labelId="invitation-default-role-label"
                label="Роль по умолчанию"
                value={draft.defaultRole}
                onChange={(event) =>
                  updateDraft({ defaultRole: event.target.value as InvitationDefaultRole })
                }
              >
                <MenuItem value="instructor">Инструктор</MenuItem>
                <MenuItem value="verified_instructor">Проверенный инструктор</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Лимит активных приглашений"
              type="number"
              value={draft.activeInvitationLimit}
              onChange={(event) => updateDraft({ activeInvitationLimit: event.target.value })}
              inputProps={{ min: 1, max: 1000, step: 1 }}
              helperText="Общий лимит ещё не принятых и не отозванных приглашений."
              disabled={isSaving}
              fullWidth
            />

            <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
              <Stack spacing={0.5}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={draft.administratorsOnly}
                      disabled
                      inputProps={{ "aria-label": "Только администраторы" }}
                    />
                  }
                  label="Только администраторы"
                />
                <Typography variant="caption" color="warning.main">
                  Обязательное правило Product Specification. Другие роли не смогут создавать или
                  управлять приглашениями.
                </Typography>
              </Stack>
            </Paper>
          </Box>

          <TextField
            label="Разрешённые email-домены"
            value={draft.allowedDomainsText}
            onChange={(event) => updateDraft({ allowedDomainsText: event.target.value })}
            placeholder={"club.example\nexample.org"}
            helperText={
              domainCount === 0
                ? "Пустой список разрешает любой домен. Указывайте домены без @, протокола и пути."
                : `В черновике доменов: ${domainCount}. Backend нормализует регистр, IDNA и дубликаты.`
            }
            minRows={4}
            multiline
            disabled={isSaving}
            fullWidth
          />

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "repeat(2, minmax(0, 1fr))" },
              gap: 2,
              minWidth: 0,
            }}
          >
            <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={draft.allowResend}
                    disabled={isSaving}
                    onChange={(event) => updateDraft({ allowResend: event.target.checked })}
                    inputProps={{ "aria-label": "Разрешить повторную отправку" }}
                  />
                }
                label="Разрешить повторную отправку"
              />
              <Typography variant="body2" color="text.secondary">
                Определяет, сможет ли будущий интерфейс повторно отправлять активное приглашение.
              </Typography>
            </Paper>

            <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={draft.requireEmailConfirmation}
                    disabled={isSaving}
                    onChange={(event) =>
                      updateDraft({ requireEmailConfirmation: event.target.checked })
                    }
                    inputProps={{ "aria-label": "Требовать подтверждение email" }}
                  />
                }
                label="Требовать подтверждение email"
              />
              <Typography variant="body2" color="text.secondary">
                Будущая регистрация должна подтвердить владение адресом до активации пользователя.
              </Typography>
            </Paper>
          </Box>

          <Paper variant="outlined" sx={{ p: 2, bgcolor: "action.hover", minWidth: 0 }}>
            <Typography variant="subtitle2">Сводка будущей политики</Typography>
            <Typography variant="body2" color="text.secondary">
              Приглашение действует {draft.expiresAfterDays || "—"} дн.; роль — {roleLabel(
                draft.defaultRole,
              )}; активный лимит — {draft.activeInvitationLimit || "—"}; домены — {domainCount || "без ограничения"}.
            </Typography>
          </Paper>

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
