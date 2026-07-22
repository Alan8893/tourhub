import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { FormEvent, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
  AccountProfile,
  AccountSession,
  changeAccountPassword,
  getAccountProfile,
  getAccountSessions,
  revokeAccountSession,
  updateAccountProfile,
} from "@/features/account/api/accountApi";
import { useAuth } from "@/features/auth/providers/AuthProvider";

interface ProfileDraft {
  displayName: string;
  phone: string;
  telegram: string;
  max: string;
  vk: string;
}

interface PasswordDraft {
  current: string;
  next: string;
  confirm: string;
}

const emptyProfile: ProfileDraft = {
  displayName: "",
  phone: "",
  telegram: "",
  max: "",
  vk: "",
};

const emptyPasswords: PasswordDraft = { current: "", next: "", confirm: "" };

function profileDraft(profile: AccountProfile): ProfileDraft {
  return {
    displayName: profile.display_name,
    phone: profile.phone ?? "",
    telegram: profile.telegram_url ?? "",
    max: profile.max_url ?? "",
    vk: profile.vk_url ?? "",
  };
}

function errorMessage(error: unknown, fallback: string): string {
  if (
    isAxiosError<{
      detail?: string | Array<{ msg?: string }>;
      error?: string;
    }>(error)
  ) {
    const payload = error.response?.data;
    if (typeof payload?.error === "string") return payload.error;
    if (typeof payload?.detail === "string") return payload.detail;
    if (Array.isArray(payload?.detail)) {
      const message = payload.detail.map((item) => item.msg).filter(Boolean).join(" ");
      if (message) return message;
    }
  }
  return error instanceof Error ? error.message : fallback;
}

function formatSessionTime(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function AccountPage() {
  const { logout, refresh } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [sessions, setSessions] = useState<AccountSession[]>([]);
  const [draft, setDraft] = useState<ProfileDraft>(emptyProfile);
  const [passwords, setPasswords] = useState<PasswordDraft>(emptyPasswords);
  const [isLoading, setIsLoading] = useState(true);
  const [isSessionsLoading, setIsSessionsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [revokingSessionId, setRevokingSessionId] = useState<number | null>(null);
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [sessionMessage, setSessionMessage] = useState<string | null>(null);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [sessionLoadError, setSessionLoadError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setLoadError(null);
    try {
      const loadedProfile = await getAccountProfile();
      setProfile(loadedProfile);
      setDraft(profileDraft(loadedProfile));
    } catch (error) {
      setLoadError(errorMessage(error, "Не удалось загрузить личный кабинет."));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadSessions() {
    setIsSessionsLoading(true);
    setSessionLoadError(null);
    try {
      setSessions(await getAccountSessions());
    } catch (error) {
      setSessionLoadError(errorMessage(error, "Не удалось загрузить активные сессии."));
    } finally {
      setIsSessionsLoading(false);
    }
  }

  useEffect(() => {
    void load();
    void loadSessions();
  }, []);

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    if (!profile) return;
    setProfileMessage(null);
    setProfileError(null);
    setIsSaving(true);
    try {
      const updated = await updateAccountProfile({
        display_name: draft.displayName,
        phone: draft.phone || null,
        telegram_url: draft.telegram || null,
        max_url: draft.max || null,
        vk_url: draft.vk || null,
        version: profile.version,
      });
      setProfile(updated);
      setDraft(profileDraft(updated));
      await refresh();
      setProfileMessage("Профиль сохранён.");
    } catch (error) {
      setProfileError(errorMessage(error, "Не удалось сохранить профиль."));
    } finally {
      setIsSaving(false);
    }
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault();
    setPasswordMessage(null);
    setPasswordError(null);
    if (passwords.next.length < 12) {
      setPasswordError("Новый пароль должен содержать не менее 12 символов.");
      return;
    }
    if (passwords.next !== passwords.confirm) {
      setPasswordError("Новый пароль и подтверждение не совпадают.");
      return;
    }
    setIsChangingPassword(true);
    try {
      const updated = await changeAccountPassword({
        current_password: passwords.current,
        new_password: passwords.next,
        new_password_confirm: passwords.confirm,
      });
      setProfile(updated);
      setPasswords(emptyPasswords);
      await Promise.all([refresh(), loadSessions()]);
      setPasswordMessage("Пароль изменён. Другие активные сессии завершены.");
    } catch (error) {
      setPasswordError(errorMessage(error, "Не удалось изменить пароль."));
    } finally {
      setIsChangingPassword(false);
    }
  }

  async function revokeSession(sessionId: number) {
    setSessionMessage(null);
    setSessionError(null);
    setRevokingSessionId(sessionId);
    try {
      await revokeAccountSession(sessionId);
      setSessions((current) => current.filter((item) => item.id !== sessionId));
      setSessionMessage("Сессия завершена.");
    } catch (error) {
      setSessionError(errorMessage(error, "Не удалось завершить сессию."));
    } finally {
      setRevokingSessionId(null);
    }
  }

  async function signOut() {
    const destination = `${location.pathname}${location.search}${location.hash}`;
    try {
      await logout();
    } finally {
      navigate("/login", { replace: true, state: { from: destination } });
    }
  }

  if (isLoading) {
    return (
      <Box sx={{ minHeight: 320, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка личного кабинета" />
      </Box>
    );
  }

  return (
    <Stack spacing={3} sx={{ maxWidth: 900, mx: "auto", minWidth: 0 }}>
      <Box>
        <Typography variant="h3" component="h1">Личный кабинет</Typography>
        <Typography color="text.secondary">
          Управление личными контактными данными, паролем и активными сессиями.
        </Typography>
      </Box>

      {loadError && (
        <Alert severity="error" action={<Button onClick={() => void load()}>Повторить</Button>}>
          {loadError}
        </Alert>
      )}

      {profile && (
        <Paper component="form" onSubmit={saveProfile} variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2.5}>
            <Box>
              <Typography variant="h5">Мой профиль</Typography>
              <Typography color="text.secondary">
                Эти контакты увидят только участники команды доступного им проекта.
              </Typography>
            </Box>
            <TextField
              label="ФИО"
              required
              value={draft.displayName}
              onChange={(event) => setDraft({ ...draft, displayName: event.target.value })}
              inputProps={{ maxLength: 120 }}
            />
            <TextField label="Почта" value={profile.email} InputProps={{ readOnly: true }} />
            <TextField
              label="Телефон"
              value={draft.phone}
              onChange={(event) => setDraft({ ...draft, phone: event.target.value })}
              placeholder="+7 999 123-45-67"
              helperText="Необязательно. В проекте номер можно открыть для звонка и сохранить через vCard."
            />
            <Divider />
            <Typography variant="subtitle1">Социальные профили</Typography>
            <Typography variant="body2" color="text.secondary">
              Можно указать никнейм или полную HTTPS-ссылку.
            </Typography>
            <TextField
              label="Telegram"
              value={draft.telegram}
              onChange={(event) => setDraft({ ...draft, telegram: event.target.value })}
              placeholder="@username или https://t.me/username"
            />
            <TextField
              label="MAX"
              value={draft.max}
              onChange={(event) => setDraft({ ...draft, max: event.target.value })}
              placeholder="username или https://max.ru/username"
            />
            <TextField
              label="VK"
              value={draft.vk}
              onChange={(event) => setDraft({ ...draft, vk: event.target.value })}
              placeholder="username или https://vk.com/username"
            />
            {profileError && <Alert severity="error">{profileError}</Alert>}
            {profileMessage && <Alert severity="success">{profileMessage}</Alert>}
            <Button type="submit" variant="contained" disabled={isSaving} sx={{ alignSelf: "flex-start" }}>
              {isSaving ? "Сохранение…" : "Сохранить профиль"}
            </Button>
          </Stack>
        </Paper>
      )}

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Активные сессии</Typography>
            <Typography color="text.secondary">
              Здесь показаны только ваши действующие входы. Текущую сессию можно завершить кнопкой выхода ниже.
            </Typography>
          </Box>
          {sessionLoadError && (
            <Alert
              severity="error"
              action={<Button onClick={() => void loadSessions()}>Повторить</Button>}
            >
              {sessionLoadError}
            </Alert>
          )}
          {isSessionsLoading ? (
            <Box sx={{ minHeight: 96, display: "grid", placeItems: "center" }}>
              <CircularProgress size={28} aria-label="Загрузка активных сессий" />
            </Box>
          ) : (
            <Stack spacing={1.5}>
              {sessions.map((session) => (
                <Paper key={session.id} variant="outlined" sx={{ p: 2, minWidth: 0 }}>
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: { xs: "column", sm: "row" },
                      alignItems: { xs: "flex-start", sm: "center" },
                      justifyContent: "space-between",
                      gap: 2,
                      minWidth: 0,
                    }}
                  >
                    <Stack spacing={0.5} sx={{ minWidth: 0 }}>
                      <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                        <Typography variant="subtitle1">Сессия №{session.id}</Typography>
                        {session.is_current && <Chip size="small" color="primary" label="Текущая" />}
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        Создана: {formatSessionTime(session.created_at)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Последняя активность: {formatSessionTime(session.last_seen_at)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Истекает: {formatSessionTime(session.expires_at)}
                      </Typography>
                    </Stack>
                    {!session.is_current && (
                      <Button
                        color="error"
                        variant="outlined"
                        disabled={revokingSessionId !== null}
                        aria-label={`Завершить сессию ${session.id}`}
                        onClick={() => void revokeSession(session.id)}
                        sx={{ flexShrink: 0 }}
                      >
                        {revokingSessionId === session.id ? "Завершение…" : "Завершить"}
                      </Button>
                    )}
                  </Box>
                </Paper>
              ))}
              {sessions.length === 0 && (
                <Typography color="text.secondary">Активные сессии не найдены.</Typography>
              )}
            </Stack>
          )}
          {sessionError && <Alert severity="error">{sessionError}</Alert>}
          {sessionMessage && <Alert severity="success">{sessionMessage}</Alert>}
        </Stack>
      </Paper>

      <Paper component="form" onSubmit={changePassword} variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2.5}>
          <Box>
            <Typography variant="h5">Смена пароля</Typography>
            <Typography color="text.secondary">
              Текущая сессия останется активной, остальные сессии будут завершены.
            </Typography>
          </Box>
          <TextField
            label="Текущий пароль"
            type="password"
            value={passwords.current}
            onChange={(event) => setPasswords({ ...passwords, current: event.target.value })}
            required
            autoComplete="current-password"
          />
          <TextField
            label="Новый пароль"
            type="password"
            value={passwords.next}
            onChange={(event) => setPasswords({ ...passwords, next: event.target.value })}
            required
            inputProps={{ minLength: 12, maxLength: 128 }}
            autoComplete="new-password"
            helperText="Не менее 12 символов."
          />
          <TextField
            label="Повторите новый пароль"
            type="password"
            value={passwords.confirm}
            onChange={(event) => setPasswords({ ...passwords, confirm: event.target.value })}
            required
            inputProps={{ minLength: 12, maxLength: 128 }}
            autoComplete="new-password"
          />
          {passwordError && <Alert severity="error">{passwordError}</Alert>}
          {passwordMessage && <Alert severity="success">{passwordMessage}</Alert>}
          <Button
            type="submit"
            variant="contained"
            disabled={isChangingPassword}
            sx={{ alignSelf: "flex-start" }}
          >
            {isChangingPassword ? "Изменение…" : "Изменить пароль"}
          </Button>
        </Stack>
      </Paper>

      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={1.5} alignItems="flex-start">
          <Typography variant="h5">Завершение работы</Typography>
          <Typography color="text.secondary">Выйти из текущей сессии на этом устройстве.</Typography>
          <Button color="error" variant="outlined" onClick={() => void signOut()}>
            Выйти
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}
