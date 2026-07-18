import { Container, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import AuthProvider, {
  AuthContext,
  AuthContextValue,
} from "@/features/auth/providers/AuthProvider";
import UserAdministrationPanel from "@/features/system-settings/components/UserAdministrationPanel";

void AuthProvider;

const auth: AuthContextValue = {
  user: {
    id: 1,
    email: "admin@tourhub.local",
    display_name: "Локальный администратор",
    role: "administrator",
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

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <AuthContext.Provider value={auth}>
        <Container maxWidth="lg" sx={{ py: 2 }}>
          <UserAdministrationPanel />
        </Container>
      </AuthContext.Provider>
    </ThemeProvider>
  </StrictMode>,
);
