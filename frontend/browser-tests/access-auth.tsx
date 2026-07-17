import { Container, CssBaseline, Paper, Stack, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import Header from "@/app/layout/Header";
import RequireAdministrator from "@/features/auth/components/RequireAdministrator";
import AuthProvider, { useAuth } from "@/features/auth/providers/AuthProvider";
import LoginPage from "@/pages/LoginPage";

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
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/settings"
              element={
                <RequireAdministrator>
                  <ProtectedSettings />
                </RequireAdministrator>
              }
            />
            <Route path="*" element={<Navigate to="/settings" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
);
