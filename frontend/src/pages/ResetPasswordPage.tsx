import {
  Alert,
  Box,
  Button,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { FormEvent, useEffect, useRef, useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import { confirmPasswordReset } from "@/features/auth/api/authApi";

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as
      | { error?: string; detail?: string; details?: Array<{ msg?: string }> }
      | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось изменить пароль.";
  }
  return "Не удалось изменить пароль.";
}

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;
    const fragment = window.location.hash.slice(1);
    const value = new URLSearchParams(fragment).get("token")?.trim() ?? "";
    setToken(value);
    if (!value) {
      setError("В ссылке отсутствует код восстановления. Запросите новую ссылку.");
    }
    if (value) {
      window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search,
      );
    }
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    if (!token) {
      setError("В ссылке отсутствует код восстановления. Запросите новую ссылку.");
      return;
    }
    if (password !== confirmation) {
      setError("Пароли не совпадают.");
      return;
    }
    setIsSubmitting(true);
    try {
      setMessage(await confirmPasswordReset({ token, password }));
      setToken("");
      setPassword("");
      setConfirmation("");
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
                Новый пароль
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                Придумайте пароль длиной от 12 до 128 символов.
              </Typography>
            </Box>
            {message && <Alert severity="success">{message}</Alert>}
            {error && <Alert severity="error">{error}</Alert>}
            {!message && (
              <>
                <TextField
                  label="Новый пароль"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete="new-password"
                  inputProps={{ minLength: 12, maxLength: 128 }}
                  disabled={isSubmitting}
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
                  disabled={isSubmitting}
                  required
                  fullWidth
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isSubmitting || !token}
                >
                  {isSubmitting ? "Сохранение…" : "Изменить пароль"}
                </Button>
              </>
            )}
            {!message && (
              <Button component={RouterLink} to="/forgot-password" variant="text">
                Запросить новую ссылку
              </Button>
            )}
            <Button component={RouterLink} to="/login" variant="text">
              Перейти ко входу
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
