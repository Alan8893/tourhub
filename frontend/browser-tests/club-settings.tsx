import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import SettingsPage from "@/pages/SettingsPage";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={createTheme()}>
        <CssBaseline />
        <SettingsPage />
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
