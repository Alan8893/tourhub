import { Container, CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import DocumentAppearanceSettingsForm from "@/features/system-settings/components/DocumentAppearanceSettingsForm";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 2 }}>
        <DocumentAppearanceSettingsForm />
      </Container>
    </ThemeProvider>
  </StrictMode>,
);
