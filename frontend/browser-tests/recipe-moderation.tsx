import { Container, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import {
  AuthContext,
  type AuthContextValue,
} from "@/features/auth/providers/AuthProvider";
import RecipesPage from "@/pages/RecipesPage";

const auth: AuthContextValue = {
  user: {
    id: 2,
    email: "reviewer@example.org",
    display_name: "Проверяющий",
    role: "verified_instructor",
    is_active: true,
    created_at: "2026-07-18T00:00:00",
  },
  bootstrapRequired: false,
  isLoading: false,
  refresh: async () => undefined,
  bootstrap: async () => undefined,
  login: async () => undefined,
  logout: async () => undefined,
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <AuthContext.Provider value={auth}>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={["/recipes"]}>
            <Container maxWidth="lg" sx={{ py: 2 }}>
              <Routes>
                <Route path="/recipes" element={<RecipesPage />} />
                <Route path="/recipes/:id" element={<RecipesPage />} />
              </Routes>
            </Container>
          </MemoryRouter>
        </QueryClientProvider>
      </AuthContext.Provider>
    </ThemeProvider>
  </StrictMode>,
);
