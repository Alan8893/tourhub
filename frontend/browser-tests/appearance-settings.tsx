import { Container, CssBaseline } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import AppearanceSettingsForm from "@/features/system-settings/components/AppearanceSettingsForm";
import AppearanceProvider from "@/features/system-settings/providers/AppearanceProvider";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <AppearanceProvider>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ py: 2 }}>
        <AppearanceSettingsForm />
      </Container>
    </AppearanceProvider>
  </StrictMode>,
);
