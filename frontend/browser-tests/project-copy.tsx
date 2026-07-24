import { Box, CssBaseline, Paper, Stack, Typography } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Route,
  Routes,
  useLocation,
  useParams,
} from "react-router-dom";

import type { ProjectCopyResponse } from "@/features/project/api/projectApi";
import ProjectCopyResultNotice from "@/features/project/components/ProjectCopyResultNotice";
import CreateProjectPage from "@/pages/CreateProjectPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

interface DestinationState {
  projectCopyResult?: ProjectCopyResponse;
}

function DestinationProbe() {
  const { id } = useParams();
  const location = useLocation();
  const state = location.state as DestinationState | null;
  const result = state?.projectCopyResult;

  return (
    <Paper sx={{ maxWidth: 760, mx: "auto", mt: 4, p: { xs: 2, sm: 3 } }}>
      <Stack spacing={2}>
        <Typography variant="h4">Новый проект #{id}</Typography>
        {result ? (
          <ProjectCopyResultNotice result={result} />
        ) : (
          <Typography>Результат копирования отсутствует.</Typography>
        )}
      </Stack>
    </Paper>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing root element");

createRoot(root).render(
  <StrictMode>
    <ThemeProvider theme={createTheme({ palette: { mode: "dark" } })}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Box sx={{ px: { xs: 1, sm: 2 } }}>
            <Routes>
              <Route path="/browser-tests/project-copy.html" element={<CreateProjectPage />} />
              <Route path="/projects/:id" element={<DestinationProbe />} />
            </Routes>
          </Box>
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  </StrictMode>,
);
