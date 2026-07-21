import { Box, CssBaseline, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode, useCallback, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import Header from "@/app/layout/Header";
import { getAccountProfile } from "@/features/account/api/accountApi";
import type { AuthUser } from "@/features/auth/api/authApi";
import { AuthContext, type AuthContextValue } from "@/features/auth/providers/AuthProvider";
import AccountPage from "@/pages/AccountPage";
import { apiClient } from "@/shared/api/client";

const initialUser: AuthUser = {
  id: 1,
  email: "irina@club.example",
  display_name: "Ирина Инструктор",
  role: "instructor",
  is_active: true,
  created_at: "2026-07-01T10:00:00Z",
};

function AccountHarness() {
  const [user, setUser] = useState<AuthUser | null>(initialUser);

  const refresh = useCallback(async () => {
    const profile = await getAccountProfile();
    setUser({
      id: profile.id,
      email: profile.email,
      display_name: profile.display_name,
      role: profile.role,
      is_active: profile.is_active,
      created_at: profile.created_at,
    });
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.post("/auth/logout");
    } finally {
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      bootstrapRequired: false,
      isLoading: false,
      refresh,
      bootstrap: async () => undefined,
      login: async () => undefined,
      logout,
    }),
    [logout, refresh, user],
  );

  return (
    <AuthContext.Provider value={value}>
      <Routes>
        <Route
          path="/account"
          element={
            <Box sx={{ minHeight: "100vh" }}>
              <Header onMenuClick={() => undefined} />
              <Box component="main" sx={{ p: { xs: 1.5, sm: 2, md: 3 } }}>
                <AccountPage />
              </Box>
            </Box>
          }
        />
        <Route path="/login" element={<Typography variant="h3">Вход после выхода</Typography>} />
      </Routes>
    </AuthContext.Provider>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme({ palette: { mode: "dark" } })}>
      <CssBaseline />
      <MemoryRouter initialEntries={["/account"]}>
        <AccountHarness />
      </MemoryRouter>
    </ThemeProvider>
  </StrictMode>,
);
