import { Container, CssBaseline } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import DishesWorkspacePage from "@/pages/DishesWorkspacePage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const root = document.getElementById("root");

if (!root) {
  throw new Error("Dish role browser acceptance root element was not found");
}

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <CssBaseline />
      <MemoryRouter initialEntries={["/dishes/dish-soup"]}>
        <Container maxWidth="lg" sx={{ py: 2 }}>
          <Routes>
            <Route path="/dishes" element={<DishesWorkspacePage />} />
            <Route path="/dishes/:id" element={<DishesWorkspacePage />} />
          </Routes>
        </Container>
      </MemoryRouter>
    </QueryClientProvider>
  </StrictMode>,
);
