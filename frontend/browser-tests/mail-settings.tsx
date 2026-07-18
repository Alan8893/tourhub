import { Container, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import MailSettingsWorkspace from "@/features/system-settings/components/MailSettingsWorkspace";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 2 }}>
        <MailSettingsWorkspace />
      </Container>
    </ThemeProvider>
  </StrictMode>,
);
