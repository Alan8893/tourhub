import { CssBaseline, Paper, Stack, Typography } from "@mui/material";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import AppLayout from "@/app/layout/AppLayout";
import ModuleVisibilityProvider from "@/features/system-settings/providers/ModuleVisibilityProvider";
import AuthTestProvider from "./auth-test-provider";

function TestPage({ title }: { title: string }) {
  return (
    <Stack spacing={2}>
      <Typography variant="h4" component="h1">{title}</Typography>
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography>
          Основной контент должен занимать всю ширину мобильного экрана, пока меню закрыто.
        </Typography>
      </Paper>
    </Stack>
  );
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("Mobile navigation browser acceptance root element was not found");
}

createRoot(root).render(
  <StrictMode>
    <CssBaseline />
    <MemoryRouter initialEntries={["/dishes"]}>
      <AuthTestProvider>
        <ModuleVisibilityProvider>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/projects" element={<TestPage title="Проекты мобильный тест" />} />
              <Route path="/dishes" element={<TestPage title="Блюда мобильный тест" />} />
              <Route path="/recipes" element={<TestPage title="Рецепты мобильный тест" />} />
              <Route path="/catalog-import" element={<TestPage title="Импорт мобильный тест" />} />
            </Route>
          </Routes>
        </ModuleVisibilityProvider>
      </AuthTestProvider>
    </MemoryRouter>
  </StrictMode>,
);
