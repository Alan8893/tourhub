import { Container, CssBaseline } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { DocumentsDownloadCard } from "@/features/documents/components/DocumentsWidget";

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <CssBaseline />
    <Container maxWidth="md" sx={{ p: 1 }}>
      <DocumentsDownloadCard projectId={76} ready />
    </Container>
  </StrictMode>,
);
