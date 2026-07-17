import { Box, Grid, Paper, Stack, TextField, Typography } from "@mui/material";

import { AppearanceColorTokens } from "../api/appearanceSettingsApi";

const COLOR_FIELDS: Array<{
  key: keyof AppearanceColorTokens;
  label: string;
  description: string;
}> = [
  { key: "primary", label: "Основной", description: "Основные действия и активные элементы." },
  { key: "secondary", label: "Дополнительный", description: "Вторичные действия." },
  { key: "accent", label: "Акцент", description: "Выделения и выбранные состояния." },
  { key: "background", label: "Фон приложения", description: "Основной фон страниц." },
  { key: "paper", label: "Фон карточек", description: "Карточки, формы и диалоги." },
  { key: "sidebar", label: "Боковое меню", description: "Фон основной навигации." },
  { key: "appbar", label: "Верхняя панель", description: "Фон шапки приложения." },
  { key: "text_primary", label: "Основной текст", description: "Обычный текст и заголовки." },
  { key: "text_secondary", label: "Вторичный текст", description: "Подсказки и пояснения." },
  { key: "divider", label: "Границы", description: "Разделители и контуры." },
  { key: "success", label: "Успех", description: "Положительные статусы." },
  { key: "warning", label: "Предупреждение", description: "Предупреждающие статусы." },
  { key: "error", label: "Ошибка", description: "Ошибки и опасные действия." },
];

interface AppearanceColorEditorProps {
  title: string;
  tokens: AppearanceColorTokens;
  disabled: boolean;
  onChange: (key: keyof AppearanceColorTokens, value: string) => void;
}

export default function AppearanceColorEditor({
  title,
  tokens,
  disabled,
  onChange,
}: AppearanceColorEditorProps) {
  return (
    <Paper variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Typography variant="h6">{title}</Typography>
        <Grid container spacing={1.5}>
          {COLOR_FIELDS.map((field) => {
            const value = tokens[field.key];
            const valid = /^#[0-9A-Fa-f]{6}$/.test(value);
            return (
              <Grid item xs={12} sm={6} key={field.key}>
                <Stack direction="row" spacing={1} alignItems="flex-start">
                  <Box
                    component="input"
                    type="color"
                    aria-label={`Выбрать цвет: ${field.label}`}
                    value={valid ? value : "#000000"}
                    disabled={disabled}
                    onChange={(event) => onChange(field.key, event.target.value.toUpperCase())}
                    sx={{
                      width: 48,
                      height: 48,
                      p: 0.25,
                      border: 1,
                      borderColor: "divider",
                      borderRadius: 1,
                      bgcolor: "background.paper",
                      cursor: disabled ? "default" : "pointer",
                    }}
                  />
                  <TextField
                    fullWidth
                    label={field.label}
                    value={value}
                    disabled={disabled}
                    error={!valid}
                    helperText={valid ? field.description : "Формат: #RRGGBB"}
                    inputProps={{ maxLength: 7 }}
                    onChange={(event) => onChange(field.key, event.target.value.toUpperCase())}
                  />
                </Stack>
              </Grid>
            );
          })}
        </Grid>
      </Stack>
    </Paper>
  );
}
