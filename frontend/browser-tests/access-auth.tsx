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
import { apiClient } from "@/shared/api/client";

function ProtectedPreparation() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = `${location.pathname}${location.search}${location.hash}`;
  return (
    <Stack spacing={2}>
      <Header onMenuClick={() => undefined} />
      <Container maxWidth="md">
        <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Typography variant="h4">Подготовка доступна</Typography>
            <Typography>Маршрут: {currentPath}</Typography>
            <Typography>{user?.display_name}</Typography>
            <Button variant="contained" onClick={() => navigate("/settings?section=users#accounts")}>
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
          <Stack spacing={2}>
            <Typography variant="h4">Настройки доступны</Typography>
            <Typography>{user?.display_name}</Typography>
            <Typography>{user?.email}</Typography>
            <Button
              variant="outlined"
              onClick={() => void apiClient.get("/session-probe").catch(() => undefined)}
            >
              Проверить сессию
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Stack>
  );
}

function ProtectedAccount() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  async function signOut() {
    const destination = `${location.pathname}${location.search}${location.hash}`;
    try {
      await logout();
    } finally {
      navigate("/login", { replace: true, state: { from: destination } });
    }
  }

  return (
    <Stack spacing={2}>
      <Header onMenuClick={() => undefined} />
      <Container maxWidth="md">
        <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
          <Stack spacing={2}>
            <Typography variant="h4">Личный кабинет доступен</Typography>
            <Typography>{user?.display_name}</Typography>
            <Typography>{user?.email}</Typography>
            <Button variant="contained" onClick={() => navigate("/settings?section=users#accounts")}>
              Открыть настройки
            </Button>
            <Button variant="outlined" color="error" onClick={() => void signOut()}>
              Выйти
            </Button>
          </Stack>
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
      <MemoryRouter initialEntries={["/projects/42?tab=menu#day-2"]}>
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
            <Route
              path="/account"
              element={
                <RequireAuthenticated>
                  <ProtectedAccount />
                </RequireAuthenticated>
              }
            />
            <Route path="*" element={<Navigate to="/projects/42" replace />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    </ThemeProvider>
  </StrictMode>,
);
