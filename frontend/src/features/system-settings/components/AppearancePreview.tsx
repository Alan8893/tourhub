import {
  Alert,
  AppBar,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Drawer,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  ThemeProvider,
  Toolbar,
  Typography,
} from "@mui/material";
import { useMemo } from "react";

import {
  AppearanceThemeDraft,
  ResolvedDisplayMode,
} from "../api/appearanceSettingsApi";
import { createTourHubTheme } from "../appearance/theme";

interface AppearancePreviewProps {
  draft: AppearanceThemeDraft;
  mode: ResolvedDisplayMode;
}

export default function AppearancePreview({ draft, mode }: AppearancePreviewProps) {
  const theme = useMemo(() => createTourHubTheme(draft, mode), [draft, mode]);

  return (
    <ThemeProvider theme={theme}>
      <Box
        sx={{
          position: "relative",
          height: { xs: 560, sm: 500 },
          overflow: "hidden",
          border: 1,
          borderColor: "divider",
          borderRadius: 2,
          bgcolor: "background.default",
          color: "text.primary",
        }}
      >
        <AppBar position="absolute" sx={{ zIndex: 3 }}>
          <Toolbar variant="dense">
            <Typography variant="subtitle1">Предпросмотр TourHub</Typography>
          </Toolbar>
        </AppBar>

        <Drawer
          variant="permanent"
          sx={{
            position: "absolute",
            width: { xs: 104, sm: 150 },
            top: 48,
            bottom: 0,
            "& .MuiDrawer-paper": {
              position: "absolute",
              width: { xs: 104, sm: 150 },
              top: 0,
              bottom: 0,
              p: 1,
            },
          }}
        >
          <Stack spacing={0.5}>
            <Button fullWidth size="small">
              Проекты
            </Button>
            <Button fullWidth size="small" variant="text">
              Блюда
            </Button>
            <Button fullWidth size="small" variant="text">
              Настройки
            </Button>
          </Stack>
        </Drawer>

        <Box
          sx={{
            position: "absolute",
            top: 48,
            left: { xs: 104, sm: 150 },
            right: 0,
            bottom: 0,
            overflow: "auto",
            p: { xs: 1.5, sm: 2 },
          }}
        >
          <Stack spacing={2}>
            <Box>
              <Typography variant="h5">Подготовка похода</Typography>
              <Typography color="text.secondary">
                Карточки, формы, таблицы и статусы используют черновик темы.
              </Typography>
            </Box>

            <Alert severity="success">Данные проекта сохранены.</Alert>

            <Card>
              <CardContent>
                <Stack spacing={1.5}>
                  <Typography variant="h6">Параметры</Typography>
                  <TextField label="Название проекта" defaultValue="Летний поход" />
                  <TextField select label="Статус" defaultValue="draft">
                    <MenuItem value="draft">Черновик</MenuItem>
                    <MenuItem value="ready">Готов</MenuItem>
                  </TextField>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                    <Button>Сохранить</Button>
                    <Button variant="outlined">Отмена</Button>
                  </Stack>
                </Stack>
              </CardContent>
            </Card>

            <Card>
              <CardContent sx={{ p: 0 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Участник</TableCell>
                      <TableCell align="right">Дни</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <TableRow>
                      <TableCell>Инструктор</TableCell>
                      <TableCell align="right">7</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Группа</TableCell>
                      <TableCell align="right">12</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
            <Divider />
          </Stack>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
