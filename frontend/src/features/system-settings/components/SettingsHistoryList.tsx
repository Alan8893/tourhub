import { Divider, List, ListItem, ListItemText, Paper, Stack, Typography } from "@mui/material";

export interface SettingsHistoryEntry {
  id: number;
  actor_label: string;
  action: string;
  changed_fields: string[];
  settings_version: number;
  created_at: string;
}

const FIELD_LABELS: Record<string, string> = {
  club_name: "название клуба",
  short_name: "краткое название",
  legal_name: "официальное название",
  description: "описание",
  address: "адрес",
  phone: "телефон",
  email: "email",
  website: "сайт",
  timezone: "часовой пояс",
  city: "город",
  region: "регион",
  social_links: "социальные сети",
  "images.main_logo": "основной логотип",
  "images.light_logo": "логотип для светлой темы",
  "images.dark_logo": "логотип для тёмной темы",
  "images.square_icon": "квадратная иконка",
  "images.favicon": "favicon",
  "images.login_background": "фон страницы входа",
  "images.document_image": "изображение для документов",
  preset_name: "предустановленная тема",
  font_family: "шрифт",
  density: "плотность интерфейса",
  border_radius: "скругление",
  button_style: "стиль кнопок",
  card_style: "стиль карточек",
  shadows_enabled: "тени",
};

function fieldLabel(field: string): string {
  if (FIELD_LABELS[field]) return FIELD_LABELS[field];
  if (field.startsWith("light.")) return `светлая тема: ${field.slice(6)}`;
  if (field.startsWith("dark.")) return `тёмная тема: ${field.slice(5)}`;
  return field;
}

interface SettingsHistoryListProps {
  items: SettingsHistoryEntry[];
}

export default function SettingsHistoryList({ items }: SettingsHistoryListProps) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={0.5}>
        <Typography variant="h6">История изменений</Typography>
        <Typography variant="body2" color="text.secondary">
          Хранятся последние 200 безопасных записей. Изображения и будущие секреты в историю
          не попадают.
        </Typography>
      </Stack>

      {items.length === 0 ? (
        <Typography sx={{ mt: 2 }} color="text.secondary">
          Изменений пока нет.
        </Typography>
      ) : (
        <List disablePadding sx={{ mt: 1 }}>
          {items.map((item, index) => (
            <Stack key={item.id}>
              {index > 0 && <Divider />}
              <ListItem disableGutters alignItems="flex-start">
                <ListItemText
                  primary={item.changed_fields.map(fieldLabel).join(", ")}
                  secondary={`${item.actor_label} · версия ${item.settings_version} · ${new Date(
                    item.created_at,
                  ).toLocaleString("ru-RU")}`}
                />
              </ListItem>
            </Stack>
          ))}
        </List>
      )}
    </Paper>
  );
}
