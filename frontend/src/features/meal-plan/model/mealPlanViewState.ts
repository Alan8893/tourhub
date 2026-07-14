export type MealPlanViewState = "loading" | "error" | "empty" | "ready";

interface MealPlanViewStateInput {
  isLoading: boolean;
  isError: boolean;
  hasMealPlan: boolean;
}

export function getMealPlanViewState({
  isLoading,
  isError,
  hasMealPlan,
}: MealPlanViewStateInput): MealPlanViewState {
  if (isLoading) return "loading";
  if (isError) return "error";
  if (!hasMealPlan) return "empty";
  return "ready";
}
