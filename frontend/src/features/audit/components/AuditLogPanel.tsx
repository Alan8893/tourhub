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
import { useCallback, useEffect, useState } from "react";

import { AuditEvent, getAuditEvents } from "../api/auditApi";

const ACTION_LABELS: Record<string, string> = {
  user_access_updated: "Доступ пользователя изменён",
  user_role_changed: "Роль пользователя изменена",
  user_reactivated: "Пользователь включён",
  user_deactivated: "Пользователь отключён",
  recipe_submitted: "Рецепт отправлен на проверку",
  recipe_published: "Рецепт опубликован",
  recipe_rejected: "Рецепт отклонён",
  project_created: "Проект создан",
  project_participants_updated: "Количество участников изменено",
  project_generation_mode_updated: "Режим рецептов проекта изменён",
  project_prepared: "Подготовка проекта выполнена",
  meal_plan_generated: "Меню сгенерировано",
  meal_slot_dish_added: "Блюдо добавлено в приём пищи",
  meal_slot_dish_removed: "Блюдо удалено из приёма пищи",
  meal_slot_dish_replaced: "Блюдо заменено в приёме пищи",
  club_settings_updated: "Настройки клуба изменены",
  appearance_settings_updated: "Оформление системы изменено",
  document_appearance_settings_updated: "Оформление документов изменено",
  module_settings_updated: "Видимость модулей изменена",
  invitation_settings_updated: "Политика приглашений изменена",
  mail_settings_updated: "Настройки почты изменены",
  mail_connection_checked: "SMTP-соединение проверено",
  mail_test_message_delivery: "Тестовая отправка почты",
  invitation_created: "Приглашение создано",
  invitation_reissued: "Приглашение перевыпущено",
  invitation_revoked: "Приглашение отозвано",
  invitation_accepted: "Приглашение принято",
  invitation_delivery_result: "Результат доставки приглашения",
};

const ENTITY_LABELS: Record<string, string> = {
  user: "Пользователь",
  recipe: "Рецепт",
  project: "Проект",
  meal_plan: "Меню",
  meal_slot: "Приём пищи",
  system_settings: "Системные настройки",
  mail: "Почта",
  invitation: "Приглашение",
};

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(new Date(value));
}

function displayValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function changedFields(event: AuditEvent): string[] {
  const before = event.before_data ?? {};
  const after = event.after_data ?? {};
  return Array.from(new Set([...Object.keys(before), ...Object.keys(after)])).filter(
    (key) => JSON.stringify(before[key]) !== JSON.stringify(after[key]),
  );
}

function AuditEventCard({ event }: { event: AuditEvent }) {
  const fields = changedFields(event);

  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, md: 2.5 }, minWidth: 0 }}>
      <Stack spacing={1.5}>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap alignItems="center">
          <Typography variant="h6">
            {ACTION_LABELS[event.action] ?? event.action}
          </Typography>
          <Chip
            size="small"
            label={ENTITY_LABELS[event.entity_type] ?? event.entity_type}
          />
          {event.entity_id && <Chip size="small" variant="outlined" label={`ID: ${event.entity_id}`} />}
        </Stack>

        <Box>
          <Typography variant="body2">
            {event.actor_display_name} · {event.actor_email}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Роль: {event.actor_role} · Actor ID: {event.actor_user_id ?? "—"} · {formatDate(event.created_at)}
          </Typography>
        </Box>

        {fields.length > 0 ? (
          <Stack spacing={0.75}>
            {fields.slice(0, 12).map((field) => (
              <Box key={field} sx={{ minWidth: 0 }}>
                <Typography variant="caption" color="text.secondary">
                  {field}
                </Typography>
                <Typography variant="body2" sx={{ overflowWrap: "anywhere" }}>
                  {displayValue(event.before_data?.[field])} → {displayValue(event.after_data?.[field])}
                </Typography>
              </Box>
            ))}
          </Stack>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Изменённые поля не указаны.
          </Typography>
        )}
      </Stack>
    </Paper>
  );
}

export default function AuditLogPanel() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [entityType, setEntityType] = useState("");
  const [action, setAction] = useState("");
  const [entityId, setEntityId] = useState("");
  const [actorUserId, setActorUserId] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getAuditEvents({
        entity_type: entityType || undefined,
        action: action.trim() || undefined,
        entity_id: entityId.trim() || undefined,
        actor_user_id: actorUserId ? Number(actorUserId) : undefined,
        limit: 100,
      });
      setEvents(response.items);
      setTotal(response.total);
    } catch {
      setError("Не удалось загрузить журнал аудита.");
    } finally {
      setIsLoading(false);
    }
  }, [action, actorUserId, entityId, entityType]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Stack spacing={3} sx={{ minWidth: 0 }}>
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <Box>
            <Typography variant="h5">Аудит действий</Typography>
            <Typography color="text.secondary">
              Неизменяемая история критичных действий с пользователями, рецептами,
              проектами, меню, системными настройками, почтой и приглашениями.
            </Typography>
          </Box>

          <Alert severity="info">
            Журнал не содержит пароли, токены сессий, приглашений или SMTP-секреты.
          </Alert>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "minmax(0, 1fr)",
                md: "repeat(2, minmax(0, 1fr))",
              },
              gap: 2,
            }}
          >
            <FormControl fullWidth>
              <InputLabel id="audit-entity-type-label">Сущность</InputLabel>
              <Select
                labelId="audit-entity-type-label"
                label="Сущность"
                value={entityType}
                onChange={(event) => setEntityType(event.target.value)}
              >
                <MenuItem value="">Все</MenuItem>
                <MenuItem value="user">Пользователь</MenuItem>
                <MenuItem value="recipe">Рецепт</MenuItem>
                <MenuItem value="project">Проект</MenuItem>
                <MenuItem value="meal_plan">Меню</MenuItem>
                <MenuItem value="meal_slot">Приём пищи</MenuItem>
                <MenuItem value="system_settings">Системные настройки</MenuItem>
                <MenuItem value="mail">Почта</MenuItem>
                <MenuItem value="invitation">Приглашение</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Действие"
              value={action}
              onChange={(event) => setAction(event.target.value)}
              placeholder="Например: invitation_delivery_result"
            />
            <TextField
              label="ID сущности"
              value={entityId}
              onChange={(event) => setEntityId(event.target.value)}
            />
            <TextField
              label="Actor ID"
              type="number"
              value={actorUserId}
              onChange={(event) => setActorUserId(event.target.value)}
              inputProps={{ min: 1 }}
            />
          </Box>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button variant="contained" onClick={() => void load()} disabled={isLoading}>
              Применить фильтры
            </Button>
            <Button
              variant="outlined"
              disabled={isLoading}
              onClick={() => {
                setEntityType("");
                setAction("");
                setEntityId("");
                setActorUserId("");
              }}
            >
              Сбросить
            </Button>
          </Stack>

          <Typography variant="body2" color="text.secondary">
            Найдено записей: {total}. Показаны последние {events.length}.
          </Typography>
          {error && <Alert severity="error">{error}</Alert>}
        </Stack>
      </Paper>

      {isLoading ? (
        <Box sx={{ py: 8, display: "grid", placeItems: "center" }}>
          <CircularProgress aria-label="Загрузка журнала аудита" />
        </Box>
      ) : events.length === 0 ? (
        <Alert severity="info">Записи по выбранным фильтрам не найдены.</Alert>
      ) : (
        <Stack spacing={2}>
          {events.map((event) => (
            <AuditEventCard key={event.id} event={event} />
          ))}
        </Stack>
      )}
    </Stack>
  );
}
