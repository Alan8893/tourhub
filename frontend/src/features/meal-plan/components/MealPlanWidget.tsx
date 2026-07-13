import { Card, CardContent, Typography } from "@mui/material";

import { MealSlotEditor, useProjectMealPlan } from "@/features/meal-slot";
import { useProjectWorkflow } from "@/features/project-workflow";

export default function MealPlanWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const { data: mealPlan, isLoading } = useProjectMealPlan(projectId);

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Meal Plan</Typography>

        <Typography sx={{ mt: 1 }}>
          {preparationResult?.meal_plan_id
            ? `✓ Meal plan created: ${preparationResult.meal_plan_id}`
            : "Menu has not been generated yet."}
        </Typography>

        {isLoading && <Typography>Loading menu...</Typography>}

        {mealPlan?.meals.map((slot) => (
          <MealSlotEditor
            key={slot.id}
            slotId={slot.id}
            mealType={`${slot.meal_type} (day ${slot.day_number})`}
            dishes={slot.dishes.map((dish) => ({
              id: dish.dish_id,
              dish_id: dish.dish_id,
              dish_name: dish.dish_name,
            }))}
          />
        ))}
      </CardContent>
    </Card>
  );
}
