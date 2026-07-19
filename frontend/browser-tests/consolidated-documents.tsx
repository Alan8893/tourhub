import { Container, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import DocumentsDownloadCard from "@/features/documents/components/DocumentsDownloadCard";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme()}>
      <CssBaseline />
      <Container maxWidth="md" sx={{ py: 2 }}>
        <DocumentsDownloadCard projectId={91} ready />
      </Container>
    </ThemeProvider>
  </StrictMode>,
);
