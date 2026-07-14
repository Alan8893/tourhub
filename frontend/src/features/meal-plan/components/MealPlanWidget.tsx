import { Alert, Card, CardContent, Divider, Stack, Typography } from "@mui/material";

import { MealSlotEditor } from "@/features/meal-slot";
import { useProjectMealPlan } from "@/features/meal-plan";
import type { MealSlot } from "@/features/meal-plan";
import { useProjectWorkflow } from "@/features/project-workflow";

const mealTypeLabels: Record<string, string> = {
  breakfast: "Завтрак",
  lunch: "Обед",
  dinner: "Ужин",
  snack: "Перекус",
};

export default function MealPlanWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const { data: mealPlan, isError, isLoading } = useProjectMealPlan(projectId);

  const groupedMeals = (mealPlan?.meals ?? []).reduce<Record<number, MealSlot[]>>(
    (acc, slot) => {
      if (!acc[slot.day_number]) {
        acc[slot.day_number] = [];
      }

      acc[slot.day_number].push(slot);
      return acc;
    },
    {},
  );

  const dayNumbers = Object.keys(groupedMeals)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Меню похода</Typography>
            <Typography variant="body2" color="text.secondary">
              {mealPlan
                ? `${mealPlan.name} · ${mealPlan.participants} участников · ${mealPlan.days_count} дней`
                : "Меню ещё не сформировано."}
            </Typography>
            {preparationResult?.meal_plan_id && !mealPlan && !isLoading && !isError && (
              <Typography variant="body2" color="success.main">
                Меню создано. Загружаем состав по дням…
              </Typography>
            )}
          </Stack>

          {isLoading && <Typography>Загрузка меню…</Typography>}

          {isError && (
            <Alert severity="error">
              Не удалось загрузить меню. Обновите страницу или повторите подготовку проекта.
            </Alert>
          )}

          {!isLoading && mealPlan && mealPlan.warnings.length > 0 && (
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Предупреждения</Typography>
              {mealPlan.warnings.map((warning) => (
                <Typography key={warning} variant="body2" color="warning.main">
                  {warning}
                </Typography>
              ))}
            </Stack>
          )}

          {!isLoading && mealPlan && dayNumbers.length === 0 && (
            <Typography variant="body2">Для этого меню пока нет приёмов пищи.</Typography>
          )}

          {!isLoading &&
            mealPlan &&
            dayNumbers.map((dayNumber, index) => (
              <Stack key={dayNumber} spacing={1.5}>
                {index > 0 && <Divider />}
                <Typography variant="subtitle1">День {dayNumber}</Typography>
                <Stack spacing={1.5}>
                  {groupedMeals[dayNumber]
                    .slice()
                    .sort((a, b) => a.meal_type.localeCompare(b.meal_type))
                    .map((slot) => (
                      <MealSlotEditor
                        key={slot.id}
                        slotId={slot.id}
                        mealType={mealTypeLabels[slot.meal_type] ?? slot.meal_type}
                        dishes={slot.dishes.map((dish) => ({
                          id: dish.dish_id,
                          dish_id: dish.dish_id,
                          dish_name: dish.dish_name,
                        }))}
                      />
                    ))}
                </Stack>
              </Stack>
            ))}
        </Stack>
      </CardContent>
    </Card>
  );
}
