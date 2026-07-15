import { Alert, Card, CardContent, Divider, Stack, Typography } from "@mui/material";

import { MealSlotEditor } from "@/features/meal-slot";
import { useProjectMealPlan } from "@/features/meal-plan";
import type { MealSlot } from "@/features/meal-plan";
import { getMealPlanViewState } from "@/features/meal-plan/model/mealPlanViewState";
import { useProjectWorkflow } from "@/features/project-workflow";

const mealTypeLabels: Record<string, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

const mealTypeOrder: Record<string, number> = {
  breakfast: 0,
  snack: 1,
  lunch: 2,
  dinner: 3,
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
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Меню похода</Typography>

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
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Предупреждения</Typography>
              {mealPlan.warnings.map((warning) => (
                <Typography key={warning} variant="body2" color="warning.main">
                  {warning}
                </Typography>
              ))}
            </Stack>
          )}

          {mealPlan && dayNumbers.length === 0 && (
            <Typography variant="body2">Для этого меню пока нет приёмов пищи.</Typography>
          )}

          {mealPlan && dayNumbers.map((dayNumber, index) => (
            <Stack key={dayNumber} spacing={1.5}>
              {index > 0 && <Divider />}
              <Typography variant="subtitle1">День {dayNumber}</Typography>
              <Stack spacing={1.5}>
                {groupedMeals[dayNumber]
                  .slice()
                  .sort(
                    (a, b) =>
                      (mealTypeOrder[a.meal_type] ?? Number.MAX_SAFE_INTEGER) -
                      (mealTypeOrder[b.meal_type] ?? Number.MAX_SAFE_INTEGER),
                  )
                  .map((slot) =>
                    slot.id.startsWith("legacy:") ? (
                      <Stack key={slot.id} spacing={0.5}>
                        <Typography variant="subtitle2">
                          {mealTypeLabels[slot.meal_type] ?? slot.meal_type}
                        </Typography>
                        {slot.dishes.map((dish) => (
                          <Typography key={dish.id} variant="body2">
                            • {dish.dish_name}
                          </Typography>
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
                        }))}
                      />
                    ),
                  )}
              </Stack>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}
