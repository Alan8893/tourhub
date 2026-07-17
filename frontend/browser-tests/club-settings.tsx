import { Container, CssBaseline } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import ClubSettingsWidget from "@/features/club-settings/components/ClubSettingsWidget";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <CssBaseline />
    <Container maxWidth="sm" sx={{ p: 1 }}>
      <ClubSettingsWidget />
    </Container>
  </StrictMode>,
);
