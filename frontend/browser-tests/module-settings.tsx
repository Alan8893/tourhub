import { Box, Button, Container, CssBaseline, Stack, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";

import Sidebar from "@/app/layout/Sidebar";
import ModuleSettingsForm from "@/features/system-settings/components/ModuleSettingsForm";
import ModuleVisibilityProvider, {
  useModuleVisibility,
} from "@/features/system-settings/providers/ModuleVisibilityProvider";
import AuthTestProvider from "./auth-test-provider";

function VisibilityProbe() {
  const { settings } = useModuleVisibility();
  return (
    <Stack spacing={0.5} aria-label="Проверка видимости карточек">
      <Typography>Меню проекта доступно</Typography>
      {settings.shopping_visible && <Typography>Карточка закупки видима</Typography>}
      {settings.equipment_visible && <Typography>Карточка оборудования видима</Typography>}
      {settings.documents_visible && <Typography>Карточка документов видима</Typography>}
    </Stack>
  );
}

function SettingsScenario() {
  const [mobileOpen, setMobileOpen] = useState(false);
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
      <Box component="main" sx={{ minWidth: 0, flex: 1 }}>
        <Container maxWidth="lg" sx={{ py: 2 }}>
          <Stack spacing={2}>
            <Button variant="outlined" onClick={() => setMobileOpen(true)}>
              Открыть мобильное меню
            </Button>
            <ModuleSettingsForm />
            <VisibilityProbe />
            <Button component={Link} to="/catalog-import" variant="outlined">
              Открыть скрытый импорт напрямую
            </Button>
          </Stack>
        </Container>
      </Box>
    </Box>
  );
}

function App() {
  return (
    <AuthTestProvider>
      <ModuleVisibilityProvider>
        <Routes>
          <Route
            path="/catalog-import"
            element={<Typography sx={{ p: 3 }}>Прямой маршрут импорта доступен</Typography>}
          />
          <Route path="*" element={<SettingsScenario />} />
        </Routes>
      </ModuleVisibilityProvider>
    </AuthTestProvider>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={createTheme()}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
