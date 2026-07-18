import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { useAuth } from "@/features/auth/providers/AuthProvider";
import {
  InvitationPublicInfo,
  acceptInvitation,
  inspectInvitation,
} from "@/features/system-settings/api/invitationSettingsApi";

interface ApiErrorBody {
  error?: string;
  detail?: string;
  details?: Array<{ msg?: string }>;
}

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось проверить приглашение.";
  }
  return "Не удалось проверить приглашение.";
}

function roleLabel(role: InvitationPublicInfo["role"]): string {
  return role === "verified_instructor" ? "Проверенный инструктор" : "Инструктор";
}

export default function AcceptInvitationPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token")?.trim() ?? "";
  const navigate = useNavigate();
  const { user, isLoading: authLoading, refresh, logout } = useAuth();
  const [invitation, setInvitation] = useState<InvitationPublicInfo | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isInspecting, setIsInspecting] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setError("В ссылке отсутствует код приглашения.");
      setIsInspecting(false);
      return;
    }
    setIsInspecting(true);
    void inspectInvitation(token)
      .then((value) => {
        setInvitation(value);
        setError(null);
      })
      .catch((inspectError) => setError(errorMessage(inspectError)))
      .finally(() => setIsInspecting(false));
  }, [token]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (!invitation) return;
    if (password !== confirmation) {
      setError("Пароли не совпадают.");
      return;
    }
    setIsSubmitting(true);
    try {
      await acceptInvitation({
        token,
        display_name: displayName,
        password,
      });
      await refresh();
      navigate("/projects", { replace: true });
    } catch (submitError) {
      setError(errorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (authLoading || isInspecting) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Проверка приглашения" />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        py: 3,
        bgcolor: "background.default",
      }}
    >
      <Container maxWidth="sm">
        <Paper variant="outlined" sx={{ p: { xs: 2.5, sm: 4 }, minWidth: 0 }}>
          <Stack spacing={2.5} component="form" onSubmit={(event) => void submit(event)}>
            <Box>
              <Typography variant="h4">TourHub</Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Принятие приглашения
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                Создайте личную учётную запись клуба по одноразовой ссылке.
              </Typography>
            </Box>

            {error && <Alert severity="error">{error}</Alert>}

            {user && (
              <Alert
                severity="warning"
                action={
                  <Button color="inherit" size="small" onClick={() => void logout()}>
                    Выйти
                  </Button>
                }
              >
                Сейчас выполнен вход как {user.display_name}. Выйдите перед принятием приглашения.
              </Alert>
            )}

            {invitation && (
              <>
                <Alert severity="info">
                  Email: {invitation.email}. Роль: {roleLabel(invitation.role)}. Ссылка действует до{" "}
                  {new Intl.DateTimeFormat("ru-RU", {
                    dateStyle: "medium",
                    timeStyle: "short",
                  }).format(new Date(invitation.expires_at))}.
                </Alert>
                <TextField label="Email" value={invitation.email} disabled fullWidth />
                <TextField
                  label="Ваше имя"
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  autoComplete="name"
                  disabled={isSubmitting || Boolean(user)}
                  required
                  fullWidth
                />
                <TextField
                  label="Пароль"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="new-password"
                  helperText="Не менее 12 символов."
                  inputProps={{ minLength: 12, maxLength: 128 }}
                  disabled={isSubmitting || Boolean(user)}
                  required
                  fullWidth
                />
                <TextField
                  label="Повторите пароль"
                  type="password"
                  value={confirmation}
                  onChange={(event) => setConfirmation(event.target.value)}
                  autoComplete="new-password"
                  inputProps={{ minLength: 12, maxLength: 128 }}
                  disabled={isSubmitting || Boolean(user)}
                  required
                  fullWidth
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isSubmitting || Boolean(user)}
                >
                  {isSubmitting ? "Создание учётной записи…" : "Принять приглашение"}
                </Button>
              </>
            )}
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
