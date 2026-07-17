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
  primary_color: "основной цвет документов",
  accent_color: "акцентный цвет документов",
  heading_color: "цвет заголовков документов",
  table_header_background: "фон заголовка таблицы",
  table_header_text: "текст заголовка таблицы",
  table_border_color: "границы таблицы",
  title_background_color: "фон титульного блока",
  logo_source: "источник логотипа документов",
  show_contacts: "отображение контактов",
  footer_text: "footer документов",
  use_document_image_as_title_background: "фоновое изображение титульного блока",
  table_density: "плотность таблиц документов",
  projects_visible: "видимость проектов",
  catalogue_visible: "видимость каталога",
  catalog_import_visible: "видимость импорта",
  shopping_visible: "видимость закупки",
  equipment_visible: "видимость оборудования",
  documents_visible: "видимость документов",
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
