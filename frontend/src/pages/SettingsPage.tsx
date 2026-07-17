import {
  Alert,
  Box,
  FormControl,
  InputLabel,
  List,
  ListItemButton,
  ListItemText,
  MenuItem,
  Paper,
  Select,
  Stack,
  Typography,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { useState } from "react";

import AppearanceSettingsForm from "@/features/system-settings/components/AppearanceSettingsForm";
import ClubSettingsForm from "@/features/system-settings/components/ClubSettingsForm";

type SettingsSectionId =
  | "club"
  | "appearance"
  | "documents"
  | "modules"
  | "invitations"
  | "mail";

const SECTIONS: Array<{
  id: SettingsSectionId;
  label: string;
  description: string;
}> = [
  {
    id: "club",
    label: "Клуб",
    description: "Название, контакты, социальные сети и изображения.",
  },
  {
    id: "appearance",
    label: "Оформление",
    description: "Светлая и тёмная темы, дизайн-токены и предпросмотр.",
  },
  {
    id: "documents",
    label: "Документы",
    description: "Отдельная палитра, footer и оформление экспортов.",
  },
  {
    id: "modules",
    label: "Модули",
    description: "Видимость модулей и контроль обязательных зависимостей.",
  },
  {
    id: "invitations",
    label: "Приглашения",
    description: "Будущие параметры приглашений до реализации пользователей.",
  },
  {
    id: "mail",
    label: "Почта",
    description: "SMTP появится после многопользовательского режима.",
  },
];

function PlannedSection({ sectionId }: { sectionId: SettingsSectionId }) {
  const section = SECTIONS.find((item) => item.id === sectionId);
  if (!section) return null;

  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
      <Stack spacing={2}>
        <Typography variant="h5">{section.label}</Typography>
        <Alert severity="info">
          Этот раздел уже заложен в структуру настроек, но будет реализован отдельным PR, чтобы
          не смешивать независимые возможности.
        </Alert>
        <Typography color="text.secondary">{section.description}</Typography>
        {sectionId === "invitations" && (
          <Typography>
            Здесь появятся срок действия, роль по умолчанию, разрешённые email-домены, повторная
            отправка, лимит активных приглашений и подтверждение email. Рабочий список приглашений
            остаётся техническим долгом до реализации пользователей.
          </Typography>
        )}
        {sectionId === "mail" && (
          <Typography>
            Планируется универсальный SMTP, секрет из environment, отдельный тестовый адрес и
            отправка фиксированного русского тестового письма. Секреты не будут возвращаться API,
            попадать в логи или незашифрованный экспорт.
          </Typography>
        )}
      </Stack>
    </Paper>
  );
}

export default function SettingsPage() {
  const theme = useTheme();
  const desktop = useMediaQuery(theme.breakpoints.up("md"));
  const [activeSection, setActiveSection] = useState<SettingsSectionId>("club");

  function sectionContent() {
    if (activeSection === "club") return <ClubSettingsForm />;
    if (activeSection === "appearance") return <AppearanceSettingsForm />;
    return <PlannedSection sectionId={activeSection} />;
  }

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Настройки</Typography>
        <Typography color="text.secondary">
          Общие настройки одной локальной установки TourHub. После появления ролей доступ будет
          ограничен администраторами.
        </Typography>
      </Box>

      {!desktop && (
        <FormControl fullWidth>
          <InputLabel id="settings-section-label">Раздел</InputLabel>
          <Select
            labelId="settings-section-label"
            label="Раздел"
            value={activeSection}
            onChange={(event) => setActiveSection(event.target.value as SettingsSectionId)}
          >
            {SECTIONS.map((section) => (
              <MenuItem key={section.id} value={section.id}>
                {section.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: desktop ? "240px minmax(0, 1fr)" : "minmax(0, 1fr)",
          gap: 3,
          alignItems: "start",
        }}
      >
        {desktop && (
          <Paper variant="outlined" sx={{ position: "sticky", top: 16 }}>
            <List disablePadding>
              {SECTIONS.map((section) => (
                <ListItemButton
                  key={section.id}
                  selected={activeSection === section.id}
                  onClick={() => setActiveSection(section.id)}
                  sx={{ alignItems: "flex-start", py: 1.5 }}
                >
                  <ListItemText
                    primary={section.label}
                    secondary={section.description}
                    secondaryTypographyProps={{ variant: "caption" }}
                  />
                </ListItemButton>
              ))}
            </List>
          </Paper>
        )}

        <Box sx={{ minWidth: 0 }}>{sectionContent()}</Box>
      </Box>
    </Stack>
  );
}
