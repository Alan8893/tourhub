import { Container, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import AuditLogPanel from "@/features/audit/components/AuditLogPanel";

const root = document.getElementById("root");
if (!root) throw new Error("Missing audit fixture root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 2 }}>
        <AuditLogPanel />
      </Container>
    </ThemeProvider>
  </StrictMode>,
);
