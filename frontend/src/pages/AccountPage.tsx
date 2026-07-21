import {
  Alert,
  Box,
  Button,
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
  ClubContact,
  changeAccountPassword,
  downloadContactVcard,
  getAccountProfile,
  getClubContacts,
  updateAccountProfile,
} from "@/features/account/api/accountApi";
import { userRoleLabel } from "@/features/auth/model/roleLabels";
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
  if (isAxiosError<{ detail?: string | Array<{ msg?: string }> }>(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const message = detail.map((item) => item.msg).filter(Boolean).join(" ");
      if (message) return message;
    }
  }
  return error instanceof Error ? error.message : fallback;
}

function ContactCard({ contact }: { contact: ClubContact }) {
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  async function saveContact() {
    setDownloadError(null);
    setIsDownloading(true);
    try {
      const blob = await downloadContactVcard(contact.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `tourhub-contact-${contact.id}.vcf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      setDownloadError(errorMessage(error, "Не удалось подготовить контакт."));
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
      <Stack spacing={1.5}>
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="h6" sx={{ overflowWrap: "anywhere" }}>
            {contact.display_name}{contact.is_current ? " · Вы" : ""}
          </Typography>
          <Typography color="text.secondary">{userRoleLabel(contact.role)}</Typography>
        </Box>
        <Button
          component="a"
          href={`mailto:${contact.email}`}
          variant="text"
          sx={{ alignSelf: "flex-start", p: 0, textTransform: "none", overflowWrap: "anywhere" }}
        >
          {contact.email}
        </Button>
        {contact.phone && (
          <Button
            component="a"
            href={`tel:${contact.phone}`}
            variant="outlined"
            sx={{ alignSelf: "flex-start", maxWidth: "100%" }}
          >
            Позвонить: {contact.phone}
          </Button>
        )}
        <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
          {contact.telegram_url && (
            <Button component="a" href={contact.telegram_url} target="_blank" rel="noreferrer">
              Telegram
            </Button>
          )}
          {contact.max_url && (
            <Button component="a" href={contact.max_url} target="_blank" rel="noreferrer">
              MAX
            </Button>
          )}
          {contact.vk_url && (
            <Button component="a" href={contact.vk_url} target="_blank" rel="noreferrer">
              VK
            </Button>
          )}
        </Stack>
        <Button
          variant="outlined"
          onClick={() => void saveContact()}
          disabled={isDownloading}
          sx={{ alignSelf: "flex-start" }}
        >
          {isDownloading ? "Подготовка…" : "Сохранить контакт"}
        </Button>
        {downloadError && <Alert severity="error">{downloadError}</Alert>}
      </Stack>
    </Paper>
  );
}

export default function AccountPage() {
  const { logout, refresh } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [contacts, setContacts] = useState<ClubContact[]>([]);
  const [draft, setDraft] = useState<ProfileDraft>(emptyProfile);
  const [passwords, setPasswords] = useState<PasswordDraft>(emptyPasswords);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  async function load() {
    setIsLoading(true);
    setLoadError(null);
    try {
      const [loadedProfile, loadedContacts] = await Promise.all([
        getAccountProfile(),
        getClubContacts(),
      ]);
      setProfile(loadedProfile);
      setDraft(profileDraft(loadedProfile));
      setContacts(loadedContacts);
    } catch (error) {
      setLoadError(errorMessage(error, "Не удалось загрузить личный кабинет."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
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
      setContacts(await getClubContacts());
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
      await refresh();
      setPasswordMessage("Пароль изменён. Другие активные сессии завершены.");
    } catch (error) {
      setPasswordError(errorMessage(error, "Не удалось изменить пароль."));
    } finally {
      setIsChangingPassword(false);
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
    <Stack spacing={3} sx={{ maxWidth: 1100, mx: "auto", minWidth: 0 }}>
      <Box>
        <Typography variant="h3" component="h1">Личный кабинет</Typography>
        <Typography color="text.secondary">
          Ваши контактные данные и контакты активных участников клуба.
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
                Почта используется для входа и доступна только для просмотра.
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
              helperText="Необязательно. После сохранения номер можно открыть для звонка и добавить через vCard."
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

      <Box>
        <Typography variant="h4" component="h2" gutterBottom>Контакты участников</Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Доступны всем вошедшим активным пользователям TourHub.
        </Typography>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "repeat(2, minmax(0, 1fr))" },
            gap: 2,
          }}
        >
          {contacts.map((contact) => <ContactCard key={contact.id} contact={contact} />)}
        </Box>
      </Box>

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
