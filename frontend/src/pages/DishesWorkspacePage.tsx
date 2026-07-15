import { Alert, AlertTitle, Box, Stack, Typography } from "@mui/material";

import { useDishCatalogueReadiness } from "@/features/dish/hooks/useDishes";
import {
  formatClassificationSummary,
  formatCoverageGap,
  formatRecommendationGap,
  getMissingRecommendedCoverage,
  getMissingRequiredCoverage,
} from "@/features/dish/model/dishCatalogueReadiness";

import DishesPage from "./DishesPage";

export default function DishesWorkspacePage() {
  const readinessQuery = useDishCatalogueReadiness();
  const readiness = readinessQuery.data;
  const missingRequired = readiness ? getMissingRequiredCoverage(readiness) : [];
  const missingRecommended = readiness ? getMissingRecommendedCoverage(readiness) : [];

  return (
    <Stack spacing={3}>
      {readinessQuery.isError && (
        <Alert severity="error">Не удалось проверить готовность каталога к автогенерации.</Alert>
      )}

      {readiness && (
        <Alert severity={readiness.ready ? "success" : "warning"}>
          <AlertTitle>
            {readiness.ready
              ? "Обязательное покрытие каталога готово"
              : "Каталог не готов к автогенерации"}
          </AlertTitle>
          <Typography variant="body2">{formatClassificationSummary(readiness)}</Typography>
          {missingRequired.length > 0 && (
            <Box component="ul" sx={{ my: 1, pl: 3 }}>
              {missingRequired.map((item) => (
                <li key={`${item.meal_type}-${item.role}`}>
                  <Typography variant="body2">{formatCoverageGap(item)}</Typography>
                </li>
              ))}
            </Box>
          )}
        </Alert>
      )}

      {readiness?.ready && missingRecommended.length > 0 && (
        <Alert severity="info">
          <AlertTitle>Рекомендуемое покрытие меню</AlertTitle>
          <Box component="ul" sx={{ my: 0, pl: 3 }}>
            {missingRecommended.map((item) => (
              <li key={`${item.meal_type}-${item.role}`}>
                <Typography variant="body2">{formatRecommendationGap(item)}</Typography>
              </li>
            ))}
          </Box>
        </Alert>
      )}

      <DishesPage />
    </Stack>
  );
}
