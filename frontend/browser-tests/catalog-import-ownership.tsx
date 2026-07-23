import { Box, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import CatalogImportPage from "@/pages/CatalogImportPage";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme({ palette: { mode: "dark" } })}>
      <CssBaseline />
      <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 1000, mx: "auto" }}>
        <CatalogImportPage />
      </Box>
    </ThemeProvider>
  </StrictMode>,
);
