import { Button, Container, CssBaseline, Paper, Stack, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  MemoryRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";

import Header from "@/app/layout/Header";
import RequireAdministrator from "@/features/auth/components/RequireAdministrator";
import RequireAuthenticated from "@/features/auth/components/RequireAuthenticated";
import AuthProvider, { useAuth } from "@/features/auth/providers/AuthProvider";
import LoginPage from "@/pages/LoginPage";

function ProtectedPreparation() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <Stack spacing={2}>
      <Header onMenuClick={() => undefined} />
      <Container maxWidth="md">
        <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Typography variant="h4">Подготовка доступна</Typography>
            <Typography>Маршрут: {location.pathname}</Typography>
            <Typography>{user?.display_name}</Typography>
            <Button variant="contained" onClick={() => navigate("/settings")}>
              Открыть настройки
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Stack>
  );
}

function ProtectedSettings() {
  const { user } = useAuth();
  return (
    <Stack spacing={2}>
      <Header onMenuClick={() => undefined} />
      <Container maxWidth="md">
        <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
          <Typography variant="h4">Настройки доступны</Typography>
          <Typography>{user?.display_name}</Typography>
          <Typography>{user?.email}</Typography>
        </Paper>
      </Container>
    </Stack>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <MemoryRouter initialEntries={["/projects/42"]}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/projects/:id"
              element={
                <RequireAuthenticated>
                  <ProtectedPreparation />
                </RequireAuthenticated>
              }
            />
            <Route
              path="/settings"
              element={
                <RequireAdministrator>
                  <ProtectedSettings />
                </RequireAdministrator>
              }
            />
            <Route path="*" element={<Navigate to="/projects/42" replace />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </ThemeProvider>
  </StrictMode>,
);
