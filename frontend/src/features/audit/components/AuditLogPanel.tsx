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

import {
  AuditEvent,
  AuditEventFilters,
  getAuditEvents,
  getAuditEventsCsv,
} from "../api/auditApi";
import { toAuditIsoTimestamp } from "../model/auditExport";

const ACTION_LABELS: Record<string, string> = {
  user_access_updated: "Доступ пользователя изменён",
  user_role_changed: "Роль пользователя изменена",
  user_reactivated: "Пользователь включён",
  user_deactivated: "Пользователь отключён",
  account_profile_updated: "Личный профиль изменён",
  account_password_changed: "Пароль пользователя изменён",
  recipe_submitted: "Рецепт отправлен на проверку",
  recipe_published: "Рецепт опубликован",
  recipe_rejected: "Рецепт отклонён",
  project_created: "Проект создан",
  project_participants_updated: "Количество участников изменено",
  project_generation_mode_updated: "Режим рецептов проекта изменён",
  project_prepared: "Подготовка проекта выполнена",
  project_instructor_added: "Инструктор добавлен в проект",
  project_instructor_removed: "Инструктор удалён из проекта",
  project_owner_transferred: "Владение проектом передано",
  project_status_updated: "Статус проекта изменён",
  project_deleted: "Проект удалён",
  meal_plan_generated: "Меню сгенерировано",
  meal_slot_dish_added: "Блюдо добавлено в приём пищи",
  meal_slot_dish_removed: "Блюдо удалено из приёма пищи",
  meal_slot_dish_replaced: "Блюдо заменено в приём пищи",
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
  product_created: "Продукт создан",
  product_updated: "Продукт изменён",
  catalog_import_applied: "Импорт каталога применён",
  purchase_list_generated: "Список закупок сформирован",
  purchase_list_updated: "Ответственный за закупки изменён",
  purchase_checklist_generated: "Чек-лист закупок сформирован",
  purchase_checklist_item_updated: "Позиция чек-листа закупок изменена",
  recipe_equipment_created: "Требование к снаряжению добавлено",
  recipe_equipment_updated: "Требование к снаряжению изменено",
  recipe_equipment_deleted: "Требование к снаряжению удалено",
  equipment_list_generated: "Список снаряжения сформирован",
  equipment_list_item_added: "Позиция снаряжения добавлена",
  equipment_list_item_updated: "Позиция снаряжения изменена",
  equipment_list_item_deleted: "Позиция снаряжения удалена",
  document_generated: "Документ сформирован",
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
  product: "Продукт",
  catalog_import: "Импорт каталога",
  purchase_list: "Список закупок",
  purchase_checklist: "Чек-лист закупок",
  purchase_checklist_item: "Позиция чек-листа",
  recipe_equipment_requirement: "Требование к снаряжению",
  equipment_list: "Список снаряжения",
  equipment_list_item: "Позиция снаряжения",
  project_document: "Документ проекта",
  purchase_list_document: "Документ закупок",
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
          {event.entity_id && (
            <Chip size="small" variant="outlined" label={`ID: ${event.entity_id}`} />
          )}
        </Stack>

        <Box>
          <Typography variant="body2">
            {event.actor_display_name} · {event.actor_email}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Роль: {event.actor_role} · Actor ID: {event.actor_user_id ?? "—"} ·{" "}
            {formatDate(event.created_at)}
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
                  {displayValue(event.before_data?.[field])} →{" "}
                  {displayValue(event.after_data?.[field])}
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
  const [createdFrom, setCreatedFrom] = useState("");
  const [createdTo, setCreatedTo] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  const currentFilters = useCallback(
    (): AuditEventFilters => ({
      entity_type: entityType || undefined,
      action: action.trim() || undefined,
      entity_id: entityId.trim() || undefined,
      actor_user_id: actorUserId ? Number(actorUserId) : undefined,
      created_from: toAuditIsoTimestamp(createdFrom),
      created_to: toAuditIsoTimestamp(createdTo),
    }),
    [action, actorUserId, createdFrom, createdTo, entityId, entityType],
  );

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getAuditEvents({
        ...currentFilters(),
        limit: 100,
      });
      setEvents(response.items);
      setTotal(response.total);
    } catch {
      setError("Не удалось загрузить журнал аудита.");
    } finally {
      setIsLoading(false);
    }
  }, [currentFilters]);

  const exportCsv = useCallback(async () => {
    setIsExporting(true);
    setExportError(null);
    try {
      const result = await getAuditEventsCsv(currentFilters());
      const url = URL.createObjectURL(result.blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = result.filename;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch {
      setExportError(
        "Не удалось выгрузить CSV. Уточните фильтры или повторите попытку.",
      );
    } finally {
      setIsExporting(false);
    }
  }, [currentFilters]);

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
              проектами, меню, каталогом, закупками, снаряжением, документами,
              системными настройками, почтой и приглашениями.
            </Typography>
          </Box>

          <Alert severity="info">
            Журнал и CSV-экспорт не содержат пароли, токены, SMTP-секреты, исходные
            CSV-файлы или содержимое сформированных документов.
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
                <MenuItem value="product">Продукт</MenuItem>
                <MenuItem value="catalog_import">Импорт каталога</MenuItem>
                <MenuItem value="purchase_list">Список закупок</MenuItem>
                <MenuItem value="purchase_checklist">Чек-лист закупок</MenuItem>
                <MenuItem value="purchase_checklist_item">
                  Позиция чек-листа
                </MenuItem>
                <MenuItem value="recipe_equipment_requirement">
                  Требование к снаряжению
                </MenuItem>
                <MenuItem value="equipment_list">Список снаряжения</MenuItem>
                <MenuItem value="equipment_list_item">Позиция снаряжения</MenuItem>
                <MenuItem value="project_document">Документ проекта</MenuItem>
                <MenuItem value="purchase_list_document">Документ закупок</MenuItem>
                <MenuItem value="system_settings">Системные настройки</MenuItem>
                <MenuItem value="mail">Почта</MenuItem>
                <MenuItem value="invitation">Приглашение</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Действие"
              value={action}
              onChange={(event) => setAction(event.target.value)}
              placeholder="Например: document_generated"
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
            <TextField
              label="С даты"
              type="datetime-local"
              value={createdFrom}
              onChange={(event) => setCreatedFrom(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="По дату"
              type="datetime-local"
              value={createdTo}
              onChange={(event) => setCreatedTo(event.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Box>

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button variant="contained" onClick={() => void load()} disabled={isLoading}>
              Применить фильтры
            </Button>
            <Button
              variant="outlined"
              onClick={() => void exportCsv()}
              disabled={isLoading || isExporting}
            >
              {isExporting ? "Готовим CSV…" : "Скачать CSV"}
            </Button>
            <Button
              variant="outlined"
              disabled={isLoading || isExporting}
              onClick={() => {
                setEntityType("");
                setAction("");
                setEntityId("");
                setActorUserId("");
                setCreatedFrom("");
                setCreatedTo("");
              }}
            >
              Сбросить
            </Button>
          </Stack>

          <Typography variant="body2" color="text.secondary">
            Найдено записей: {total}. Показаны последние {events.length}.
          </Typography>
          {error && <Alert severity="error">{error}</Alert>}
          {exportError && <Alert severity="error">{exportError}</Alert>}
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
