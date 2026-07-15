import { CssBaseline, Container } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import MealSlotEditor from "@/features/meal-slot/components/MealSlotEditor";

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
      <CssBaseline />
      <Container maxWidth={false} sx={{ p: 1 }}>
        <MealSlotEditor
          slotId="slot-1"
          mealType="Обед"
          dishes={[
            {
              id: "slot-dish-1",
              dish_id: "dish-porridge",
              dish_name: "Овсяная каша",
            },
            {
              id: "slot-dish-2",
              dish_id: "dish-tea",
              dish_name: "Чай",
            },
          ]}
        />
      </Container>
    </QueryClientProvider>
  </StrictMode>,
);
