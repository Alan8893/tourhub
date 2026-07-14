import { Card, CardContent, Divider, Stack, Typography } from "@mui/material";

import { MealSlotEditor } from "@/features/meal-slot";
import { useProjectMealPlan } from "@/features/meal-plan";
import type { MealSlot } from "@/features/meal-plan";
import { useProjectWorkflow } from "@/features/project-workflow";

const mealTypeLabels: Record<string, string> = {
  breakfast: "Breakfast",
  lunch: "Lunch",
  dinner: "Dinner",
  snack: "Snack",
};

export default function MealPlanWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const { data: mealPlan, isLoading } = useProjectMealPlan(projectId);

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
            <Typography variant="h6">Meal Plan</Typography>
            <Typography variant="body2" color="text.secondary">
              {mealPlan
                ? `${mealPlan.name} · ${mealPlan.participants} participants · ${mealPlan.days_count} days`
                : "Menu has not been generated yet."}
            </Typography>
            {preparationResult?.meal_plan_id && (
              <Typography variant="body2" color="success.main">
                Meal plan created: {preparationResult.meal_plan_id}
              </Typography>
            )}
          </Stack>

          {isLoading && <Typography>Loading menu...</Typography>}

          {!isLoading && mealPlan && mealPlan.warnings.length > 0 && (
            <Stack spacing={0.5}>
              <Typography variant="subtitle2">Warnings</Typography>
              {mealPlan.warnings.map((warning) => (
                <Typography key={warning} variant="body2" color="warning.main">
                  {warning}
                </Typography>
              ))}
            </Stack>
          )}

          {!isLoading && mealPlan && dayNumbers.length === 0 && (
            <Typography variant="body2">No meal slots available for this plan.</Typography>
          )}

          {!isLoading && mealPlan &&
            dayNumbers.map((dayNumber, index) => (
              <Stack key={dayNumber} spacing={1.5}>
                {index > 0 && <Divider />}
                <Typography variant="subtitle1">Day {dayNumber}</Typography>
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
