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
import { useCallback, useEffect, useState } from "react";

import {
  InvitationDefaultRole,
  InvitationDeliveryStatus,
  InvitationRecord,
  InvitationStatus,
  createInvitation,
  listInvitations,
  reissueInvitation,
  revokeInvitation,
} from "../api/invitationSettingsApi";

interface Props {
  defaultRole: InvitationDefaultRole;
  allowReissue: boolean;
}

interface ApiErrorBody {
  error?: string;
  detail?: string;
  details?: Array<{ msg?: string }>;
}

interface DeliveryNotice {
  status: InvitationDeliveryStatus;
  message: string;
  attempts: number;
}

const STATUS_LABELS: Record<InvitationStatus, string> = {
  active: "Активно",
  expired: "Истекло",
  revoked: "Отозвано",
  consumed: "Принято",
  superseded: "Заменено",
};

function roleLabel(role: InvitationDefaultRole): string {
  return role === "verified_instructor" ? "Проверенный инструктор" : "Инструктор";
}

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось выполнить действие.";
  }
  return "Не удалось выполнить действие.";
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function linkFor(path: string): string {
  return `${window.location.origin}${path}`;
}

function deliverySeverity(status: InvitationDeliveryStatus): "success" | "warning" | "error" {
  if (status === "sent") return "success";
  if (status === "unavailable") return "warning";
  return "error";
}

export default function InvitationLifecyclePanel({ defaultRole, allowReissue }: Props) {
  const [records, setRecords] = useState<InvitationRecord[]>([]);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<InvitationDefaultRole>(defaultRole);
  const [lastLink, setLastLink] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [delivery, setDelivery] = useState<DeliveryNotice | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionId, setActionId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      setRecords(await listInvitations());
    } catch (loadError) {
      setError(errorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    setRole(defaultRole);
  }, [defaultRole]);

  async function create() {
    if (!email.trim()) {
      setError("Укажите email пользователя.");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    setMessage(null);
    setDelivery(null);
    try {
      const created = await createInvitation({ email, role });
      setLastLink(linkFor(created.acceptance_path));
      setEmail("");
      setDelivery({
        status: created.delivery_status,
        message: created.delivery_message,
        attempts: created.delivery_attempts,
      });
      setMessage("Приглашение создано. Ручная ссылка доступна независимо от доставки.");
      await load();
    } catch (createError) {
      setError(errorMessage(createError));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function reissue(record: InvitationRecord) {
    setActionId(record.id);
    setError(null);
    setMessage(null);
    setDelivery(null);
    try {
      const replacement = await reissueInvitation(record.id);
      setLastLink(linkFor(replacement.acceptance_path));
      setDelivery({
        status: replacement.delivery_status,
        message: replacement.delivery_message,
        attempts: replacement.delivery_attempts,
      });
      setMessage("Создана новая ссылка. Предыдущая ссылка больше не действует.");
      await load();
    } catch (actionError) {
      setError(errorMessage(actionError));
    } finally {
      setActionId(null);
    }
  }

  async function revoke(record: InvitationRecord) {
    setActionId(record.id);
    setError(null);
    setMessage(null);
    setDelivery(null);
    try {
      await revokeInvitation(record.id);
      setMessage("Приглашение отозвано.");
      await load();
    } catch (actionError) {
      setError(errorMessage(actionError));
    } finally {
      setActionId(null);
    }
  }

  async function copyLink() {
    if (!lastLink) return;
    try {
      await navigator.clipboard.writeText(lastLink);
      setMessage("Ссылка скопирована в буфер обмена.");
    } catch {
      setMessage("Скопируйте ссылку из поля вручную.");
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 }, minWidth: 0 }}>
      <Stack spacing={2.5}>
        <Box>
          <Typography variant="h5">Рабочие приглашения</Typography>
          <Typography color="text.secondary">
            TourHub создаёт одноразовую ссылку и автоматически пытается отправить её по email. При любой проблеме ссылка остаётся доступной для ручной передачи.
          </Typography>
        </Box>

        <Alert severity="info">
          Исходная ссылка показывается только сразу после создания или повторного выпуска. В базе данных хранится только необратимый отпечаток.
        </Alert>
        {error && <Alert severity="error">{error}</Alert>}
        {message && <Alert severity="success">{message}</Alert>}
        {delivery && (
          <Alert severity={deliverySeverity(delivery.status)}>
            {delivery.message} Попыток: {delivery.attempts}.
          </Alert>
        )}

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "minmax(0, 1fr)", md: "minmax(0, 2fr) minmax(0, 1fr) auto" },
            gap: 2,
            alignItems: "start",
            minWidth: 0,
          }}
        >
          <TextField
            label="Email пользователя"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={isSubmitting}
            required
            fullWidth
          />
          <FormControl fullWidth disabled={isSubmitting}>
            <InputLabel id="new-invitation-role-label">Роль</InputLabel>
            <Select
              labelId="new-invitation-role-label"
              label="Роль"
              value={role}
              onChange={(event) => setRole(event.target.value as InvitationDefaultRole)}
            >
              <MenuItem value="instructor">Инструктор</MenuItem>
              <MenuItem value="verified_instructor">Проверенный инструктор</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            disabled={isSubmitting}
            onClick={() => void create()}
            sx={{ minHeight: 56 }}
          >
            {isSubmitting ? "Создание…" : "Создать ссылку"}
          </Button>
        </Box>

        {lastLink && (
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1} alignItems="stretch">
            <TextField
              label="Новая ссылка приглашения"
              value={lastLink}
              InputProps={{ readOnly: true }}
              fullWidth
            />
            <Button variant="outlined" onClick={() => void copyLink()}>
              Копировать
            </Button>
          </Stack>
        )}

        <Typography variant="h6">История приглашений</Typography>
        {isLoading ? (
          <Box sx={{ py: 4, display: "grid", placeItems: "center" }}>
            <CircularProgress aria-label="Загрузка приглашений" />
          </Box>
        ) : records.length === 0 ? (
          <Alert severity="info">Приглашений пока нет.</Alert>
        ) : (
          <Stack spacing={1.5}>
            {records.map((record) => {
              const canReissue = allowReissue && (record.status === "active" || record.status === "expired");
              const busy = actionId === record.id;
              return (
                <Paper key={record.id} variant="outlined" sx={{ p: 2, minWidth: 0 }}>
                  <Stack spacing={1.25}>
                    <Stack
                      direction={{ xs: "column", sm: "row" }}
                      spacing={1}
                      justifyContent="space-between"
                      alignItems={{ xs: "flex-start", sm: "center" }}
                    >
                      <Box sx={{ minWidth: 0 }}>
                        <Typography fontWeight={600} sx={{ overflowWrap: "anywhere" }}>
                          {record.email}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {roleLabel(record.role)} · до {formatDate(record.expires_at)}
                        </Typography>
                      </Box>
                      <Chip label={STATUS_LABELS[record.status]} size="small" />
                    </Stack>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                      <Button
                        variant="outlined"
                        disabled={!canReissue || busy}
                        onClick={() => void reissue(record)}
                      >
                        Выпустить новую ссылку
                      </Button>
                      <Button
                        color="error"
                        variant="outlined"
                        disabled={record.status !== "active" || busy}
                        onClick={() => void revoke(record)}
                      >
                        Отозвать
                      </Button>
                    </Stack>
                  </Stack>
                </Paper>
              );
            })}
          </Stack>
        )}
      </Stack>
    </Paper>
  );
}
