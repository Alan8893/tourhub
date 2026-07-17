import { CssBaseline } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import AppearanceProvider from "@/features/system-settings/providers/AppearanceProvider";
import SettingsPage from "@/pages/SettingsPage";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <AppearanceProvider>
        <CssBaseline />
        <SettingsPage />
      </AppearanceProvider>
    </BrowserRouter>
  </StrictMode>,
);
