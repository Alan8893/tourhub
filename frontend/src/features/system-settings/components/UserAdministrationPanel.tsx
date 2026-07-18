import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  FormControlLabel,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  Switch,
  Typography,
} from "@mui/material";
import axios from "axios";
import { useCallback, useEffect, useState } from "react";

import type { UserRole } from "@/features/auth/api/authApi";
import { userRoleLabel } from "@/features/auth/model/roleLabels";
import { useAuth } from "@/features/auth/providers/AuthProvider";
import {
  ManagedUser,
  listManagedUsers,
  updateManagedUser,
} from "../api/userAdministrationApi";

interface ApiErrorBody {
  error?: string;
  detail?: string;
  details?: Array<{ msg?: string }>;
}

function formatDate(value: string | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function errorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    const details = body?.details?.map((item) => item.msg).filter(Boolean).join(" ");
    return details || body?.detail || body?.error || "Не удалось сохранить пользователя.";
  }
  return "Не удалось сохранить пользователя.";
}

interface UserCardProps {
  user: ManagedUser;
  onSaved: (user: ManagedUser) => Promise<void>;
  onConflict: () => Promise<void>;
}

function UserCard({ user, onSaved, onConflict }: UserCardProps) {
  const [role, setRole] = useState<UserRole>(user.role);
  const [isActive, setIsActive] = useState(user.is_active);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const changed = role !== user.role || isActive !== user.is_active;

  useEffect(() => {
    setRole(user.role);
    setIsActive(user.is_active);
    setError(null);
  }, [user]);

  async function save() {
    if (!changed) return;
    const removesAdministrator =
      user.role === "administrator" && (role !== "administrator" || !isActive);
    const deactivatesUser = user.is_active && !isActive;
    if (
      (removesAdministrator || deactivatesUser) &&
      !window.confirm(
        removesAdministrator
          ? "Подтвердите понижение роли или отключение администратора."
          : "Подтвердите отключение пользователя. Все его активные сессии будут завершены.",
      )
    ) {
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      const updated = await updateManagedUser(user.id, {
        expected_version: user.version,
        role,
        is_active: isActive,
      });
      await onSaved(updated);
    } catch (saveError) {
      if (axios.isAxiosError(saveError) && saveError.response?.status === 409) {
        setError(errorMessage(saveError));
        await onConflict();
      } else {
        setError(errorMessage(saveError));
      }
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, md: 2.5 }, minWidth: 0 }}>
      <Stack spacing={2}>
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Typography variant="h6" sx={{ overflowWrap: "anywhere" }}>
              {user.display_name}
            </Typography>
            {user.is_current && <Chip label="Текущая учётная запись" size="small" />}
            {!user.is_active && <Chip label="Отключён" size="small" color="warning" />}
          </Stack>
          <Typography color="text.secondary" sx={{ overflowWrap: "anywhere" }}>
            {user.email}
          </Typography>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "minmax(0, 1fr)", sm: "minmax(0, 1fr) auto" },
            gap: 2,
            alignItems: "center",
            minWidth: 0,
          }}
        >
          <FormControl fullWidth disabled={isSaving}>
            <InputLabel id={`user-role-${user.id}`}>Роль</InputLabel>
            <Select
              labelId={`user-role-${user.id}`}
              label="Роль"
              value={role}
              onChange={(event) => setRole(event.target.value as UserRole)}
            >
              <MenuItem value="administrator">Администратор</MenuItem>
              <MenuItem value="instructor">Инструктор</MenuItem>
              <MenuItem value="verified_instructor">Проверенный инструктор</MenuItem>
            </Select>
          </FormControl>
          <FormControlLabel
            control={
              <Switch
                checked={isActive}
                onChange={(event) => setIsActive(event.target.checked)}
                disabled={isSaving}
                inputProps={{ "aria-label": `Активен ${user.email}` }}
              />
            }
            label="Активен"
          />
        </Box>

        <Typography variant="body2" color="text.secondary">
          Роль: {userRoleLabel(user.role)}. Последний вход: {formatDate(user.last_login_at)}. Версия: {user.version}.
        </Typography>

        <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
          <Button
            variant="outlined"
            disabled={isSaving || !changed}
            onClick={() => {
              setRole(user.role);
              setIsActive(user.is_active);
              setError(null);
            }}
          >
            Отменить
          </Button>
          <Button variant="contained" disabled={isSaving || !changed} onClick={() => void save()}>
            {isSaving ? "Сохранение…" : "Сохранить пользователя"}
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
}

export default function UserAdministrationPanel() {
  const { refresh } = useAuth();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setUsers(await listManagedUsers());
    } catch {
      setError("Не удалось загрузить пользователей.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleSaved(updated: ManagedUser) {
    setUsers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    setSuccess("Изменения пользователя сохранены.");
    if (updated.is_current) await refresh();
  }

  if (isLoading) {
    return (
      <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Загрузка пользователей" />
      </Box>
    );
  }

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={1.5}>
          <Typography variant="h5">Пользователи</Typography>
          <Typography color="text.secondary">
            Администраторы управляют ролями и доступом. Отключение немедленно завершает активные сессии пользователя.
          </Typography>
          <Alert severity="info">
            TourHub не позволит отключить или понизить последнего активного администратора.
          </Alert>
          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}
        </Stack>
      </Paper>

      {users.length === 0 ? (
        <Alert severity="warning">Пользователи не найдены.</Alert>
      ) : (
        <Stack spacing={2}>
          {users.map((user) => (
            <UserCard
              key={`${user.id}:${user.version}`}
              user={user}
              onSaved={handleSaved}
              onConflict={load}
            />
          ))}
        </Stack>
      )}
    </Stack>
  );
}
