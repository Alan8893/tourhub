import { Container, CssBaseline } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ProjectWorkflowProvider } from "@/features/project-workflow";
import { PurchaseWidget } from "@/features/purchase";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const root = document.getElementById("root");

if (!root) {
  throw new Error("Browser acceptance root element was not found");
}

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ProjectWorkflowProvider projectId={71}>
        <CssBaseline />
        <Container maxWidth="md" sx={{ p: 1 }}>
          <PurchaseWidget />
        </Container>
      </ProjectWorkflowProvider>
    </QueryClientProvider>
  </StrictMode>,
);
