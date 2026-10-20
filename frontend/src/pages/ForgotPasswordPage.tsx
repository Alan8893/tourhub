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
import { FormEvent, useState } from "react";
import { Link as RouterLink } from "react-router-dom";

import { requestPasswordReset } from "@/features/auth/api/authApi";

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as
      | { error?: string; detail?: string; details?: Array<{ msg?: string }> }
      | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось отправить запрос. Попробуйте позже.";
  }
  return "Не удалось отправить запрос. Попробуйте позже.";
}

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setError(null);
    setIsSubmitting(true);
    try {
      setMessage(await requestPasswordReset({ email }));
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
                Восстановление пароля
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>
                Укажите email, связанный с учётной записью.
              </Typography>
            </Box>
            {message && <Alert severity="success">{message}</Alert>}
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              disabled={isSubmitting || Boolean(message)}
              required
              fullWidth
            />
            <Button type="submit" variant="contained" size="large" disabled={isSubmitting || Boolean(message)}>
              {isSubmitting ? "Отправка…" : "Отправить инструкцию"}
            </Button>
            <Button component={RouterLink} to="/login" variant="text">
              Вернуться ко входу
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
