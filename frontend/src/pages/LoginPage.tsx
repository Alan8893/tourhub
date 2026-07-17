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
import { FormEvent, useMemo, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "@/features/auth/providers/AuthProvider";

interface LocationState {
  from?: string;
}

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as
      | { error?: string; detail?: string; details?: Array<{ msg?: string }> }
      | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось выполнить вход.";
  }
  return "Не удалось выполнить вход.";
}

export default function LoginPage() {
  const { user, bootstrapRequired, isLoading, bootstrap, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const destination = useMemo(
    () => (location.state as LocationState | null)?.from || "/projects",
    [location.state],
  );
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isLoading) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Проверка конфигурации доступа" />
      </Box>
    );
  }

  if (user) return <Navigate to={destination} replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (bootstrapRequired && password !== confirmation) {
      setError("Пароли не совпадают.");
      return;
    }
    setIsSubmitting(true);
    try {
      if (bootstrapRequired) {
        await bootstrap({ email, display_name: displayName, password });
      } else {
        await login({ email, password });
      }
      navigate(destination, { replace: true });
    } catch (submitError) {
      setError(errorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
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
          <Stack component="form" spacing={2.5} onSubmit={(event) => void submit(event)}>
            <Box>
              <Typography variant="h4">TourHub</Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                {bootstrapRequired ? "Создание первого администратора" : "Вход"}
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                {bootstrapRequired
                  ? "Этот шаг выполняется один раз для локальной установки клуба."
                  : "Используйте учётную запись TourHub."}
              </Typography>
            </Box>

            {bootstrapRequired && (
              <Alert severity="info">
                Первый пользователь получит роль «Администратор». Повторный bootstrap будет
                заблокирован сервером.
              </Alert>
            )}
            {error && <Alert severity="error">{error}</Alert>}

            {bootstrapRequired && (
              <TextField
                label="Имя администратора"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                autoComplete="name"
                disabled={isSubmitting}
                required
                fullWidth
              />
            )}
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              disabled={isSubmitting}
              required
              fullWidth
            />
            <TextField
              label="Пароль"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete={bootstrapRequired ? "new-password" : "current-password"}
              helperText={bootstrapRequired ? "Не менее 12 символов." : undefined}
              inputProps={{ minLength: 12, maxLength: 128 }}
              disabled={isSubmitting}
              required
              fullWidth
            />
            {bootstrapRequired && (
              <TextField
                label="Повторите пароль"
                type="password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                autoComplete="new-password"
                inputProps={{ minLength: 12, maxLength: 128 }}
                disabled={isSubmitting}
                required
                fullWidth
              />
            )}

            <Button type="submit" variant="contained" size="large" disabled={isSubmitting}>
              {isSubmitting
                ? "Сохранение…"
                : bootstrapRequired
                  ? "Создать администратора"
                  : "Войти"}
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
