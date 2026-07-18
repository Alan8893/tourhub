import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from "@mui/material";

import { MealSlotEditor } from "@/features/meal-slot";
import { formatDishCount } from "@/features/meal-slot/model/mealSlotEditorState";
import { useProjectMealPlan } from "@/features/meal-plan";
import type { MealSlot } from "@/features/meal-plan";
import {
  countMealPlanDayDishes,
  getMealPlanViewState,
  isMealPlanDayExpandedByDefault,
  sortMealSlots,
} from "@/features/meal-plan/model/mealPlanViewState";
import { useProjectWorkflow } from "@/features/project-workflow";

const mealTypeLabels: Record<string, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

export default function MealPlanWidget() {
  const { projectId } = useProjectWorkflow();
  const { data: mealPlan, isError, isLoading } = useProjectMealPlan(projectId);
  const viewState = getMealPlanViewState({
    isLoading,
    isError,
    hasMealPlan: Boolean(mealPlan),
  });

  const groupedMeals = (mealPlan?.meals ?? []).reduce<Record<number, MealSlot[]>>(
    (acc, slot) => {
      if (!acc[slot.day_number]) acc[slot.day_number] = [];
      acc[slot.day_number].push(slot);
      return acc;
    },
    {},
  );
  const dayNumbers = Object.keys(groupedMeals).map(Number).sort((a, b) => a - b);

  return (
    <Card sx={{ width: "100%" }}>
      <CardContent>
        <Stack spacing={2}>
          <Stack spacing={0.25}>
            <Typography variant="h6">Меню похода</Typography>
            <Typography variant="body2" color="text.secondary">
              Дни можно сворачивать, чтобы быстрее просматривать длинное меню. Для каждого блюда показан сохранённый вариант рецепта.
            </Typography>
          </Stack>

          {viewState === "loading" && <Typography>Загрузка меню…</Typography>}

          {viewState === "error" && (
            <Alert severity="error">
              Не удалось загрузить меню из-за ошибки сервера. Обновите страницу и повторите попытку.
            </Alert>
          )}

          {viewState === "empty" && (
            <Typography variant="body2" color="text.secondary">
              Меню ещё не сформировано. Нажмите «Сформировать меню» в блоке следующего действия.
            </Typography>
          )}

          {mealPlan && (
            <Typography variant="body2" color="text.secondary">
              {mealPlan.name} · участников: {mealPlan.participants} · дней: {mealPlan.days_count}
            </Typography>
          )}

          {mealPlan && mealPlan.warnings.length > 0 && (
            <Stack spacing={1}>
              {mealPlan.warnings.map((warning) => (
                <Alert key={warning} severity="warning">
                  {warning}
                </Alert>
              ))}
            </Stack>
          )}

          {mealPlan && dayNumbers.length === 0 && (
            <Typography variant="body2">Для этого меню пока нет приёмов пищи.</Typography>
          )}

          {mealPlan && (
            <Stack spacing={1}>
              {dayNumbers.map((dayNumber, index) => {
                const dayMeals = sortMealSlots(groupedMeals[dayNumber]);
                const dishCount = countMealPlanDayDishes(dayMeals);
                const contentId = `meal-plan-day-${dayNumber}-content`;
                const headerId = `meal-plan-day-${dayNumber}-header`;

                return (
                  <Accordion
                    key={dayNumber}
                    defaultExpanded={isMealPlanDayExpandedByDefault(index)}
                    disableGutters
                    elevation={0}
                    sx={{
                      border: 1,
                      borderColor: "divider",
                      borderRadius: 1,
                      "&:before": { display: "none" },
                    }}
                  >
                    <AccordionSummary
                      id={headerId}
                      aria-controls={contentId}
                      expandIcon={<Typography component="span" aria-hidden="true">⌄</Typography>}
                    >
                      <Stack
                        direction="row"
                        spacing={1}
                        alignItems="center"
                        justifyContent="space-between"
                        sx={{ width: "100%", pr: 1 }}
                      >
                        <Typography variant="subtitle1" component="h3">
                          День {dayNumber}
                        </Typography>
                        <Chip size="small" variant="outlined" label={formatDishCount(dishCount)} />
                      </Stack>
                    </AccordionSummary>
                    <AccordionDetails id={contentId} sx={{ pt: 0 }}>
                      <Stack spacing={1.5}>
                        {dayMeals.map((slot) =>
                          slot.id.startsWith("legacy:") ? (
                            <Stack key={slot.id} spacing={0.5}>
                              <Typography variant="subtitle2">
                                {mealTypeLabels[slot.meal_type] ?? slot.meal_type}
                              </Typography>
                              {slot.dishes.map((dish) => (
                                <Stack key={dish.id} spacing={0}>
                                  <Typography variant="body2">• {dish.dish_name}</Typography>
                                  <Typography variant="caption" color="text.secondary" sx={{ pl: 2 }}>
                                    Рецепт: {dish.recipe_name}
                                  </Typography>
                                </Stack>
                              ))}
                            </Stack>
                          ) : (
                            <MealSlotEditor
                              key={slot.id}
                              slotId={slot.id}
                              mealType={mealTypeLabels[slot.meal_type] ?? slot.meal_type}
                              dishes={slot.dishes.map((dish) => ({
                                id: dish.id,
                                dish_id: dish.dish_id,
                                dish_name: dish.dish_name,
                                recipe_id: dish.recipe_id,
                                recipe_name: dish.recipe_name,
                              }))}
                            />
                          ),
                        )}
                      </Stack>
                    </AccordionDetails>
                  </Accordion>
                );
              })}
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
